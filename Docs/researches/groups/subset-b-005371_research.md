# subset-b-005371 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_aoss.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_aoss.c

## Purpose

`qcom_aoss.c` implements the Qualcomm Always-On Subsystem QMP mailbox driver. It maps AOSS message RAM, performs the QMP link/channel handshake, exports `qmp_send()` and `qmp_get()/qmp_put()` to other drivers, registers a QDSS clock provider, optional thermal cooling devices, and debugfs write-only controls for AOSS sleep, CX collapse, DDR collapse, and DDR frequency requests.

## Important APIs, Types, and Functions

The central state is `struct qmp`, holding the message RAM mapping, mailbox channel, negotiated mailbox offset/size, waitqueue, TX mutex, clock hw, cooling devices, and debugfs dentries. `qmp_open()` validates `QMP_MAGIC`/`QMP_VERSION`, reads MCORE mailbox location, acknowledges UCORE link state, raises local link/channel state, kicks AOSS, and waits for ACKs. `qmp_send()` serializes formatted string messages into the message RAM and waits until the remote side clears the message length. Exported helpers are `qmp_send()`, `qmp_get()`, and `qmp_put()`. Integration helpers include `qmp_qdss_clk_add/remove()`, `qmp_cooling_devices_register/remove()`, and `qmp_debugfs_create()`.

## Control Flow

Probe allocates `struct qmp`, maps the first platform resource, requests mailbox channel 0 and the AOSS interrupt, opens the QMP link, registers the QDSS clock, registers cooling devices for child nodes with `#cooling-cells`, stores drvdata, and creates debugfs files. Interrupts simply wake the QMP waitqueue; all protocol progress is driven by wait conditions reading message RAM state. Remove tears down debugfs, clock provider, cooling devices, QMP state, and mailbox channel. `qmp_send()` writes the 64-byte payload after the length word, writes the length, readbacks for ordering, kicks AOSS, then waits up to one second for `qmp_message_empty()`.

## State and Persistence Behavior

Driver state is volatile and per platform device. AOSS-visible state is shared in message RAM: link-state words, channel-state words, mailbox offset/size, and the current outbound message. Persistent hardware effects are indirect: QMP messages can change AOSS-managed clock, thermal, and low-power behavior. Debugfs writes and cooling-device state cache the last requested boolean locally, but authoritative effect is in AOSS firmware.

## Dependencies and Integration Points

The driver depends on platform resources, mailbox framework, IRQ wakeups, MMIO accessors, clock provider APIs, thermal cooling devices, debugfs, device tree phandles, and tracepoints. `qcom_stats.c` uses `qmp_get()` and `qmp_send()` to synchronize DDR stats. Other Qualcomm clients can use the exported QMP API if their DT node has `qcom,qmp`.

## Risks and Edge Cases

`qmp_send()` always writes `sizeof(buf)` as the message length, not the formatted length, so the remote protocol must expect fixed 64-byte padded messages. Timeout handling clears the length word locally, which may race with delayed remote consumption. `qmp_cooling_devices_remove()` iterates a fixed two-entry array even when no cooling devices were registered; `qmp->cooling_devs` can be NULL if there were no child cooling nodes. `qmp_cooling_devices_register()` increments `count` without checking more than two eligible child nodes. Debugfs message construction relies on file dentry identity matching the stored dentry array. Link open failures leave link/channel state down but depend on firmware responding to the final kick.

## Test Signals

Useful tests include probe with invalid magic/version/zero mailbox size, mailbox request failure, IRQ timeout during each handshake phase, concurrent `qmp_send()` callers, long debugfs inputs, QDSS prepare/unprepare, cooling-device state changes, `qmp_get()` before and after probe, remove with no cooling devices, and AOSS firmware that delays or drops message acknowledgments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_aoss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_gsbi.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_gsbi.c

## Purpose

`qcom_gsbi.c` configures the Qualcomm GSBI wrapper used by older SoCs to route a serial block to SPI, UART, I2C, or other protocols and to program TCSR CRCI mux bits for ADM DMA routing. After programming the wrapper, it populates child devices below the GSBI node.

## Important APIs, Types, and Functions

`struct gsbi_info` holds the enabled interface clock, selected protocol mode, CRCI field, and optional TCSR regmap. `struct crci_config` and SoC tables (`config_ipq8064`, `config_apq8064`, `config_msm8960`, `config_msm8660`) encode per-GSBI ADM CRCI masks. `gsbi_probe()` is the only runtime function. The DT match table binds `qcom,gsbi-v1.0.0`, while TCSR syscon nodes are matched by `qcom,tcsr-*`.

## Control Flow

Probe maps the GSBI register, optionally resolves `syscon-tcsr`, reads `cell-index`, validates it is 1 through 12, reads `qcom,mode`, optionally reads `qcom,crci`, enables the `iface` clock, writes `(mode << 4) | crci` to `GSBI_CTRL_REG`, updates matching TCSR CRCI bits to zero for SPI and to the mask for other modes, issues a write memory barrier, stores drvdata, and calls `of_platform_populate()` for child controllers.

## State and Persistence Behavior

The driver keeps only probe-lifetime state through devm resources and drvdata. Hardware state persists in the GSBI control register and optional TCSR CRCI registers until reset or later firmware/kernel writes. There is no remove callback and no attempt to restore prior TCSR settings.

## Dependencies and Integration Points

It depends on DT properties `cell-index`, `qcom,mode`, optional `qcom,crci`, optional `syscon-tcsr`, the `iface` clock, MMIO, regmap/syscon, and child platform population. The protocol values come from `dt-bindings/soc/qcom,gsbi.h`; child serial drivers depend on this wrapper being configured before their probe.

## Risks and Edge Cases

Missing TCSR is tolerated, so DMA CRCI routing can remain firmware/default configured. `regmap_update_bits()` failures are ignored, which can hide broken syscon mappings. The CRCI mask arrays assume `cell-index - 1` maps directly to table columns. Because there is no remove path, unbinding the driver will not disable the clock or depopulate children beyond devm cleanup behavior.

## Test Signals

Test DTs should cover every supported TCSR compatible, missing/invalid `cell-index`, missing `qcom,mode`, optional `qcom,crci`, SPI versus non-SPI CRCI behavior, failed clock enable, child population, and register readback of GSBI/TCSR values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_gsbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pd_mapper.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pd_mapper.c

## Purpose

`qcom_pd_mapper.c` implements an in-kernel Qualcomm Protection Domain Mapper service. It exposes a QRTR/QMI SERVREG LOC server that answers domain-list requests for known SoC protection domains and acknowledges local process-failure-reason reports. Its goal is to replace or supplement a userspace pd-mapper daemon on platforms with static domain topology.

## Important APIs, Types, and Functions

`struct qcom_pdm_domain_data` describes one domain, instance id, and associated service names. Runtime objects are `qcom_pdm_data`, `qcom_pdm_service`, and `qcom_pdm_domain`. `qcom_pdm_add_domain()` builds a service-to-domains list, always registering the domain under `tms/servreg` and additionally under listed services. `qcom_pdm_get_domain_list()` handles `SERVREG_GET_DOMAIN_LIST_REQ`; `qcom_pdm_pfr()` handles `SERVREG_LOC_PFR_REQ`. `qcom_pdm_start()` selects the current machine from `qcom_pdm_domains`, initializes `qmi_handle`, adds static domains, and registers the QMI server.

## Control Flow

The auxiliary driver binds to `qcom_common.pd-mapper`. Probe serializes global startup under `qcom_pdm_mutex`; the first probe calls `qcom_pdm_start()` and later probes increment a refcount. QMI message dispatch is provided by `qmi_interface.c` using `qcom_pdm_msg_handlers`. For domain-list requests, the handler computes the requested offset, looks up the service, fills response metadata, copies up to `SERVREG_DOMAIN_LIST_LENGTH` domains, sends a QMI response, then frees the response. Remove decrements the refcount and shuts down the QMI handle only when the last auxiliary device goes away.

## State and Persistence Behavior

State is global and process-lifetime: `__qcom_pdm_data` points to the singleton QMI server and service list. Domain data itself is static read-only tables selected by SoC compatible. There is no persistent storage; responses reflect the baked-in table, not runtime remoteproc discovery. Refcounting allows multiple auxiliary devices to share one server.

## Dependencies and Integration Points

It depends on auxiliary bus, `of_machine_get_match()`, QRTR/QMI helpers, message descriptors from `qcom_pdr_msg.c` and `pdr_internal.h`, and Qualcomm common auxiliary device creation elsewhere. Remote clients discover the server via QMI service id `QMI_SERVICE_ID_SERVREG_LOC`, version `0x101`, instance 0.

## Risks and Edge Cases

The pagination condition uses `i < SERVREG_DOMAIN_LIST_LENGTH` rather than comparing `i - offset` against the response capacity, so nonzero offsets can prematurely return no entries or too few entries. `strscpy()` uses `sizeof(rsp->domain_list[i].name)` while writing index `j`; sizes are the same, but the index mismatch is fragile. `qcom_pdm_add_domain()` does not roll back earlier service registrations if a later service add fails. Unsupported machines return `-ENODEV`, forcing userspace to provide the service. Static tables can become stale as firmware service naming changes.

## Test Signals

Tests should cover machine match selection, duplicate service/domain rejection, multiple auxiliary probes/removes, domain-list requests for `tms/servreg`, audio/GPS/WLAN services, nonzero offsets, unknown service names, PFR requests, QRTR net reset behavior through `qmi_handle`, and memory-failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pd_mapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pdr_msg.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pdr_msg.c

## Purpose

`qcom_pdr_msg.c` is a descriptor-only module for Qualcomm SERVREG/PDR QMI messages. It exports `struct qmi_elem_info` arrays consumed by the generic QMI encoder/decoder and by protection-domain clients such as `qcom_pd_mapper.c`.

## Important APIs, Types, and Functions

The file exports descriptors for domain-list request/response, listener registration request/response, restart-PD request/response, service-state update indications, ACK request/response, and local PFR request/response. `servreg_location_entry_ei` is the nested descriptor for domain list entries. Most descriptors pair optional-valid flags with matching optional values and use `qmi_response_type_v01_ei` for common response status.

## Control Flow

There is no executable protocol control flow beyond module load. At runtime, callers pass these arrays to `qmi_encode_message()` or `qmi_decode_message()`. The descriptor order matters: optional flags must precede the data with the same TLV type, data length descriptors must precede variable-length arrays, and nested structures point to their own descriptor arrays.

## State and Persistence Behavior

All state is static const descriptor data exported to other modules. The file has no private mutable state and no hardware or file persistence. Persistent protocol behavior comes from keeping these descriptors ABI-compatible with remote SERVREG firmware.

## Dependencies and Integration Points

It depends on `<linux/soc/qcom/qmi.h>` for descriptor schema constants and on `pdr_internal.h` for message structure definitions, sizes, message ids, and enum types. Integration points are all QMI clients/servers handling protection-domain restart, service registry lookup, and PDR listener state.

## Risks and Edge Cases

Descriptor mistakes are runtime ABI bugs, not compile-time type errors. `servreg_loc_pfr_req_ei` marks strings as `VAR_LEN_ARRAY` without a preceding `QMI_DATA_LEN`, unlike many variable arrays; correctness depends on the QMI string handling path rather than normal array-length handling. Some enum fields use `sizeof(u32)` rather than the enum type while other descriptors use enum size. Fixed string limits must leave room for the decoder's NUL terminator.

## Test Signals

Round-trip tests should encode/decode every exported message type, including optional fields present and absent, max-length names/reasons, zero-length variable lists, maximum `SERVREG_DOMAIN_LIST_LENGTH` responses, and unknown optional TLVs. Integration tests should exercise the descriptors through `qcom_pd_mapper.c` QMI request handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pdr_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_stats.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_stats.c

## Purpose

`qcom_stats.c` exposes Qualcomm RPM/RPMh sleep and DDR low-power statistics through debugfs. It reads SoC sleep stats from MSG RAM/MMIO, subsystem sleep stats from SMEM items, and optional DDR stats after synchronizing newer platforms through AOSS QMP.

## Important APIs, Types, and Functions

`struct stats_config` captures per-compatible offsets, record counts, appended-vote availability, dynamic RPM offset behavior, and whether subsystem stats live in SMEM. `struct sleep_stats`, `struct appended_stats`, and `struct ddr_stats_entry` mirror firmware data. Show paths are `qcom_soc_sleep_stats_show()`, `qcom_subsystem_sleep_stats_show()`, and `qcom_ddr_stats_show()`. Creation helpers build debugfs files for subsystem, SoC sleep, and DDR stats. `qcom_stats_probe()` maps the resource, gets optional QMP, creates `qcom_stats`, and marks PM not required.

## Control Flow

Probe selects config from OF match data, maps resource 0, allocates one `stats_data` per record, optionally resolves QMP, creates the debugfs directory, creates subsystem files if enabled, creates one file per low-power mode by reading each record's stat-type name from MMIO, and creates `ddr_stats` only when the DDR magic key matches. Reads copy the relevant shared record each time; DDR reads may first send `{class: ddr, action: freqsync}` over QMP.

## State and Persistence Behavior

Kernel state is limited to debugfs dentries, per-record MMIO pointers, and the global optional `qcom_stats_qmp`. Statistics are firmware-maintained counters in MSG RAM or SMEM and persist across driver reads. Accumulated duration is adjusted at read time if a subsystem is currently sleeping by adding the current arch timer delta.

## Dependencies and Integration Points

Dependencies include platform MMIO, debugfs, SMEM, AOSS QMP, arm arch timer, device tree compatibles, and bitfield helpers. It integrates with `qcom_aoss.c` for DDR stats sync and `smem.c` for subsystem statistics.

## Risks and Edge Cases

`qcom_stats_qmp` is global, so multiple instances would overwrite one another. `qcom_stats_remove()` removes debugfs but does not call `qmp_put()`, despite `qmp_get()` taking a device reference. Dynamic offsets are read from firmware and used without checking that computed records fit in the mapped resource. Debugfs file names are derived from raw four-byte stat types; unexpected bytes can create odd names. `devm_platform_get_and_ioremap_resource()` errors are collapsed to `-ENOMEM`, losing probe diagnostics.

## Test Signals

Validate each compatible config, dynamic RPM offset parsing, fixed RPM offsets, subsystem SMEM item absence, DDR magic mismatch, QMP absent/present/deferred/error paths, active sleep duration adjustment, malformed DDR entry count greater than 20, debugfs teardown, and repeated DDR reads that require QMP sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_encdec.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_encdec.c

## Purpose

`qmi_encdec.c` is the generic Qualcomm QMI TLV encoder/decoder. It translates C structures described by `struct qmi_elem_info` arrays to and from QMI wire messages with `struct qmi_header`, endian conversion, nested structures, strings, optional TLVs, static arrays, and variable-length arrays.

## Important APIs, Types, and Functions

Exported APIs are `qmi_encode_message()`, `qmi_decode_message()`, and `qmi_response_type_v01_ei`. Internal helpers include `qmi_calc_min_msg_len()`, `qmi_encode_basic_elem()`, `qmi_encode_struct_elem()`, `qmi_encode_string_elem()`, `qmi_encode()`, `qmi_decode_basic_elem()`, `qmi_decode_struct_elem()`, `qmi_decode_string_elem()`, `find_ei()`, and `qmi_decode()`. Macro helpers encode/decode TLV headers and little-endian integer widths.

## Control Flow

Encoding starts at `qmi_encode_message()`, optionally validates NULL payloads against minimum message length, allocates header plus caller-provided max length, recursively encodes top-level TLVs, fills header type/txn/message id/message length, and updates `*len`. Top-level fields reserve TLV header space before payload; nested fields omit TLV headers. Optional flags determine whether all fields with the same TLV type are skipped. Decoding verifies inputs, then walks TLVs until the payload is consumed; required unknown TLVs fail, unknown optional TLVs are skipped, known TLVs are decoded into C offsets.

## State and Persistence Behavior

The module has no mutable state. Allocation state is limited to encoded message buffers returned to callers, who must free them. Decoding writes into caller-provided output structures. Protocol persistence depends entirely on descriptor stability and QMI peers.

## Dependencies and Integration Points

It depends on Linux allocation, endian helpers, string handling, kernel logging, and `<linux/soc/qcom/qmi.h>`. It is the codec backend for `qmi_interface.c`, `qcom_pdr_msg.c`, `qcom_pd_mapper.c`, and other Qualcomm QMI clients.

## Risks and Edge Cases

Several pointer operations are on `void *`, relying on compiler extensions used by the kernel. `qmi_decode_message()` does not check `len >= sizeof(struct qmi_header)` before subtracting, so too-short messages can underflow size. `qmi_encode_string_elem()` uses `strlen()` on source buffers, requiring C-string termination even for fixed QMI string fields. `qmi_decode_string_elem()` rejects `string_len >= elem_len`, so max-capacity strings require descriptors to include terminator space. Descriptor errors around optional flags or `QMI_DATA_LEN` can desynchronize subsequent fields.

## Test Signals

Round-trip tests should cover all integer widths, signed enums, nested structs, static arrays, variable arrays with 8-bit and 16-bit lengths, optional fields omitted and present, strings at boundary lengths, unknown optional TLVs, unknown required TLVs, zero-length messages, too-short headers, undersized output buffers, and malformed data lengths larger than descriptor limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_encdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_interface.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_interface.c

## Purpose

`qmi_interface.c` provides the kernel-side Qualcomm QMI transport over QRTR sockets. It manages service lookup/advertisement, transactions, message dispatch, QRTR control packets, socket reset handling, workqueue-driven receive processing, and send helpers for requests, responses, and indications.

## Important APIs, Types, and Functions

Exported APIs include `qmi_add_lookup()`, `qmi_add_server()`, `qmi_txn_init()`, `qmi_txn_wait()`, `qmi_txn_cancel()`, `qmi_handle_init()`, `qmi_handle_release()`, `qmi_send_request()`, `qmi_send_response()`, and `qmi_send_indication()`. Internal paths handle QRTR `NEW_SERVER`, `DEL_SERVER`, `BYE`, `DEL_CLIENT`, net reset, message dispatch, and socket creation. Runtime state lives in `struct qmi_handle`: socket, locks, IDR of transactions, workqueue, receive buffer, service lists, lookup results, callbacks, and handlers.

## Control Flow

`qmi_handle_init()` initializes locks, IDR, service lists, work item, handlers, receive buffer, ordered workqueue, and QRTR socket. Socket data-ready callbacks queue work. `qmi_data_ready_work()` drains datagrams; control packets update callbacks/service lists, ENETRESET recreates the socket and reannounces lookups/services, and normal packets either use a raw `msg_handler` callback or the QMI transaction/handler dispatcher. Responses match `txn_id` in the IDR; requests and indications use a temporary transaction object carrying the incoming id. Send helpers encode messages with `qmi_encode_message()` and send over the QRTR socket under `sock_lock`.

## State and Persistence Behavior

State is volatile per QMI handle. Lookups and advertised services remain in lists and are replayed after QRTR net reset. Lookup results are dynamically allocated and freed on `DEL_SERVER`, `BYE`, net reset, or release. Transactions live from `qmi_txn_init()` until wait/cancel. There is no file persistence.

## Dependencies and Integration Points

The file depends on QRTR sockets, kernel networking, IDR, mutexes, completions, ordered workqueues, QMI codec functions, and `qmi_ops`/`qmi_msg_handler` definitions. It is used by QMI clients/servers such as the protection-domain mapper and remote service consumers.

## Risks and Edge Cases

`qmi_handle_release()` assumes `qmi->sock` is valid and dereferences it before locking. Transaction wait/cancel removes the IDR entry while receive dispatch may already hold the transaction lock; the locking is intentional but requires callers not to free transaction storage before wait/cancel returns. `qmi_add_lookup()` and `qmi_add_server()` do not deduplicate registrations. Receive buffer size is caller-controlled plus header, so undersized values can still decode-fail. On ENETRESET, callbacks are invoked while service lists are being rebuilt; client callbacks must tolerate reorder and loss.

## Test Signals

Tests should cover socket creation failure and `-EAFNOSUPPORT`, lookup/server registration replay after net reset, transaction success, timeout and cancel, unexpected response ids, malformed short packets, raw `msg_handler` override, all QRTR control packet types, concurrent send and release, QMI handler decode failures, and service callback allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ramp_controller.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/ramp_controller.c

## Purpose

`ramp_controller.c` programs the Qualcomm Ramp Controller on MSM8976-class hardware. The controller handles hardware-managed ramp-up/down behavior after SoC-specific SID configuration is written.

## Important APIs, Types, and Functions

`struct qcom_ramp_controller_desc` stores SoC-specific register sequences for DFS, link, LMH, enable, disable, counts, and command-register offset. `struct qcom_ramp_controller` stores the regmap and selected descriptor. Core helpers are `rc_wait_for_update()`, `rc_set_cfg_update()`, `rc_write_cfg()`, `rc_ramp_ctrl_enable()`, and `qcom_ramp_controller_start()`. Probe/remove perform MMIO regmap setup and start/disable sequences.

## Control Flow

Probe maps MMIO, allocates state, fetches OF match data, initializes a 32-bit regmap, stores drvdata, and calls `qcom_ramp_controller_start()`. Start writes LMH SIDs, DFS SIDs, link SIDs, then enables ramp control. Each config write waits for controller readiness, writes a reg sequence, and triggers config updates from the last SID downward. Remove writes the disable sequence and logs if it fails.

## State and Persistence Behavior

Driver state is devm-managed. Hardware state persists in ramp-controller registers after probe; the driver has no runtime management beyond disabling on remove. There is no software cache of current register values.

## Dependencies and Integration Points

The driver depends on platform MMIO, regmap, OF match data, initcall ordering, and hard-coded MSM8976 register sequences. It suppresses bind attrs, implying dynamic unbind/rebind is not intended as a normal control path.

## Risks and Edge Cases

`rc_set_cfg_update()` writes `ce` with `regmap_set_bits()`, which treats `ce` as a bitmask, not an arbitrary field value; this matches only if configuration-entry numbers are bit positions or low bits intended by hardware. The ack computation uses `FIELD_PREP(RC_CFG_ACK, BIT(ce))`; large `ce` values could overflow the 16-bit ack field, though current constants fit. Remove cannot recover from a failed disable sequence. Adding SoCs requires exact sequence counts and register limits.

## Test Signals

Tests should include successful probe register trace, timeout in readiness and ACK polling, failed regmap writes, remove disable sequence, invalid/missing match data, and hardware readback that confirms each SID update and final enable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ramp_controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rmtfs_mem.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/rmtfs_mem.c

## Purpose

`rmtfs_mem.c` exposes a reserved memory region for Qualcomm remote filesystem use as `/dev/qcom_rmtfs_mem<client_id>` plus sysfs attributes. It allows userspace remote-filesystem daemons to read, write, and mmap modem-owned shared memory and optionally assigns SCM VM permissions.

## Important APIs, Types, and Functions

`struct qcom_rmtfs_mem` embeds `struct device` and `struct cdev`, the write-combined mapping, physical address, size, client id, and SCM permission mask. File operations implement open/read/write/release/mmap. Sysfs attributes expose `phys_addr`, `size`, and `client_id`. Probe parses reserved memory, `qcom,client-id`, optional guard pages, optional `qcom,vmid`, creates the cdev device, maps memory, and performs `qcom_scm_assign_mem()` when requested.

## Control Flow

Module init registers class, allocates a char-dev major range, and registers the platform driver. Probe locates reserved memory, trims guard pages if requested, initializes the embedded device, maps the region with `MEMREMAP_WC`, registers the cdev, parses up to two VMIDs, and if VMIDs are present assigns the memory to HLOS plus those VMs with RW permissions. Reads/writes clamp count at region size and copy to/from the mapped memory. Mmap remaps the physical range with write-combine protection. Remove reassigns memory to HLOS when permissions were changed, deletes the cdev, and drops the device reference.

## State and Persistence Behavior

The reserved memory contents persist independently of the driver and are visible to remote firmware/userspace. Driver state persists while the platform device exists. SCM permission changes affect secure world memory ownership until remove reassigns them or the system resets.

## Dependencies and Integration Points

Dependencies include reserved-memory DT, char device core, custom class, sysfs, memremap, mmap remapping, copy_to/from_user, and Qualcomm SCM. It integrates with remote filesystem userspace and remote processors expecting the shared physical memory and client id.

## Risks and Edge Cases

Guard-page trimming subtracts 8 KiB without checking the reserved region is large enough. Client ids map directly to device minor numbers; invalid ids above `MINORMASK` are not explicitly rejected before `MKDEV()`. Read/write arithmetic uses `*f_pos + count`, which can overflow `loff_t`/size_t combinations. No locking protects concurrent readers/writers. VMID parsing with zero elements and absent property relies on OF return conventions.

## Test Signals

Test reserved-memory absence, missing client id, small guard-page regions, invalid client ids, read/write at boundaries and EOF, mmap larger than region, SCM unavailable/deferred/failure paths, permission reassignment on remove, cdev registration failure, and concurrent open/remove lifetime handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rmtfs_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm-proc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm-proc.c

## Purpose

`rpm-proc.c` is a small platform driver that represents the Qualcomm RPM processor/subsystem node. It optionally registers an SMD edge described by a `smd-edge` child and populates child devices below the RPM processor node.

## Important APIs, Types, and Functions

`rpm_proc_probe()` and `rpm_proc_remove()` are the only runtime functions. Probe uses `of_get_child_by_name()`, `qcom_smd_register_edge()`, `devm_of_platform_populate()`, and stores the optional `struct qcom_smd_edge *` as drvdata. The driver binds `qcom,rpm-proc`.

## Control Flow

Probe looks for a `smd-edge` child. If present, it registers the edge and handles errors with `dev_err_probe()`. It then populates child platform devices. If child population fails after edge registration, the edge is unregistered. Remove unregisters the edge if one exists. Registration uses `arch_initcall` so RPM infrastructure is available early for dependent child devices.

## State and Persistence Behavior

The driver owns only the optional SMD edge handle and child device population. There is no persistent storage or hardware state mutation in this file beyond registering the communication edge with the SMD/rpmsg infrastructure.

## Dependencies and Integration Points

It depends on OF platform population and Qualcomm SMD rpmsg helpers. It is an integration parent for RPM child drivers such as SMD RPM, regulators, clocks, and other resources under the RPM processor DT node.

## Risks and Edge Cases

If no `smd-edge` child exists, the driver still populates children; those children must not assume an edge exists unless their DT requires it. Devm child population is automatic, but explicit SMD edge unregister must stay paired with registration. Probe deferral comes from edge registration or child population.

## Test Signals

Test with and without `smd-edge`, failed edge registration, failed child population after edge registration, remove ordering, and initcall ordering with child drivers that depend on RPM communication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm_master_stats.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm_master_stats.c

## Purpose

`rpm_master_stats.c` exposes Qualcomm RPM Master Stats v2 records through debugfs. Each configured MSG RAM slice is mapped and displayed under `qcom_rpm_master_stats/<master-name>`.

## Important APIs, Types, and Functions

`struct rpm_master_stats` mirrors the packed firmware record: active cores, shutdown count, shutdown/bringup/wakeup timestamps, wakeup reason, transition durations, and XO shutdown counters. `struct master_stats_data` carries one mapped base and label. `master_stats_show()` copies a record from IO memory and prints fields. Probe parses `qcom,master-names` and matching `qcom,rpm-msg-ram` phandles.

## Control Flow

Probe counts master names, allocates data entries, creates the debugfs root, then for each index parses the MSG RAM phandle, maps resource 0 with `devm_ioremap()`, reads the matching label, and creates a debugfs file. Remove recursively removes the debugfs tree.

## State and Persistence Behavior

State is read-only debug mapping state. Stats are maintained by RPM firmware in MSG RAM and persist across debugfs reads. The driver has no writes and no file-backed persistence.

## Dependencies and Integration Points

It depends on OF phandles, `of_address_to_resource()`, debugfs, IO memory mapping, and platform driver binding to `qcom,rpm-master-stats`. There is intentionally no module device table, so it is a manually loaded debugging module.

## Risks and Edge Cases

The driver treats debugfs creation failure as fatal because debugfs is its only purpose. It maps shared resources manually rather than using platform helpers. Count mismatches between `qcom,master-names` and phandles fail at the first missing phandle. The packed layout must match firmware exactly.

## Test Signals

Test zero/missing master names, missing MSG RAM phandles, mapping failure, debugfs creation failure, multiple masters, field readout consistency, remove cleanup, and module autoload expectations given the intentional lack of `MODULE_DEVICE_TABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm_master_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-internal.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-internal.h

## Purpose

`rpmh-internal.h` is the private contract between the Qualcomm RPMh client layer (`rpmh.c`) and Resource State Coordinator driver (`rpmh-rsc.c`). It defines TCS sizing, controller/request state, and internal function prototypes.

## Important APIs, Types, and Functions

Constants define four TCS types, at most 16 commands per TCS, at most three TCSes per type, and derived slot counts. `struct tcs_group` describes one TCS group, including type, mask, offset, command slots, and active request pointers. `struct rpmh_request` wraps a `tcs_request`, inline command storage, optional completion, device, and free flag. `struct rpmh_ctrlr` stores cached sleep/wake requests and dirty state. `struct rsc_drv` stores MMIO bases, version, TCS groups, locks, waitqueue, PM notifiers, and embedded RPMh client state.

## Control Flow

The header declares the cross-file flow: `rpmh.c` sends active requests with `rpmh_rsc_send_data()`, writes sleep/wake control data with `rpmh_rsc_write_ctrl_data()`, invalidates TCS slots with `rpmh_rsc_invalidate()`, asks RSC to write next wakeup, and receives completion via `rpmh_tx_done()`. `rpmh-rsc.c` calls `rpmh_flush()` during low-power transitions.

## State and Persistence Behavior

All state is volatile kernel state reflecting RPMh hardware programming. Cached requests in `rpmh_ctrlr` persist for the life of an RSC controller and are flushed into sleep/wake TCS hardware before low-power entry. TCS register contents persist until invalidated, overwritten, or reset.

## Dependencies and Integration Points

It depends on bitmap helpers, waitqueues, and `<soc/qcom/tcs.h>`. It is not a public API; external clients use `<soc/qcom/rpmh.h>` while this header coordinates private implementation details.

## Risks and Edge Cases

The lock-order comment is important: `rsc_drv.lock` before `rpmh_ctrlr.cache_lock`. Violating it can deadlock PM flush and active transfer paths. Array sizes (`MAX_TCS_PER_TYPE`, `MAX_RPMH_PAYLOAD`) must remain consistent with hardware and public TCS definitions. `slots` is only valid for sleep/wake TCSes, while `req[]` is only for active transfers.

## Test Signals

Compile tests should catch structure drift across `rpmh.c` and `rpmh-rsc.c`. Runtime tests should stress active transfers, borrowed wake TCSes, sleep/wake cache flush, dirty-cache handling, PM callbacks, and lockdep for documented lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-rsc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-rsc.c

## Purpose

`rpmh-rsc.c` is the Qualcomm RPMh Resource State Coordinator driver. It discovers RSC/TCS hardware, programs Trigger Command Sets, handles active-transfer completion IRQs, writes cached sleep/wake votes before low-power transitions, and populates RPMh child devices.

## Important APIs, Types, and Functions

Public-to-internal functions are `rpmh_rsc_send_data()`, `rpmh_rsc_write_ctrl_data()`, `rpmh_rsc_invalidate()`, and `rpmh_rsc_write_next_wakeup()`. Key helpers include register offset tables for RSC versions 2.7 and 3.0, TCS register accessors, `tcs_invalidate()`, `get_tcs_for_msg()`, `tcs_tx_done()`, `__tcs_buffer_write()`, `check_for_req_inflight()`, `claim_tcs_for_req()`, `find_slots()`, PM callbacks, `rpmh_probe_tcs_config()`, and `rpmh_rsc_probe()`.

## Control Flow

Probe waits for command DB readiness, allocates `struct rsc_drv`, reads `qcom,drv-id` and label, maps the named `drv-N` resource, reads RSC version, selects register offsets, parses `qcom,tcs-offset` and `qcom,tcs-config`, initializes locks and waitqueue, requests the per-DRV IRQ, installs CPU PM or genpd notifiers unless hardware solver mode is present, enables active TCS IRQs, initializes RPMh caches, stores drvdata, and populates children. Active requests claim a free non-conflicting TCS under lock, write commands, and trigger AMC mode. IRQ completion clears trigger/enable, releases TCS ownership, wakes waiters, and calls `rpmh_tx_done()`. Sleep/wake requests are written into slots without triggering and are used by firmware during low power entry.

## State and Persistence Behavior

Driver state tracks TCS group ownership, software in-use bits, slot bitmaps, active request pointers, cached RPMh client votes, and PM notifier state. Hardware TCS command registers persist until invalidated or overwritten. `rpmh_rsc_write_next_wakeup()` writes control-TCS wakeup timestamp data for low-power coordination.

## Dependencies and Integration Points

It depends on platform resources, command DB, DT TCS configuration, IRQs, CPU PM, genpd, PM runtime, arch timer, RPMh internal API, TCS public definitions, and child platform devices. Client drivers under the RSC use `rpmh.c` APIs to submit votes.

## Risks and Edge Cases

`rpmh_rsc_send_data()` waits indefinitely for a free TCS; missing interrupts can hang callers. Borrowed wake TCSes for active transfers require careful invalidation before later wake usage. PM callbacks rely on being the last CPU or serialized genpd transition and require interrupts disabled for `rpmh_flush()`. TCS config validation must match hardware; bad DT can miscompute masks and offsets. There is no explicit remove path to unregister CPU PM notifiers for dynamically removed devices, likely mitigated by suppressing bind attrs and initcall-style platform use.

## Test Signals

Test RSC version selection, invalid `qcom,tcs-config`, active transfer completion, TCS exhaustion, same-address conflict waiting, missing active TCS with wake borrowing, sleep/wake flush, batch slot exhaustion, CPU PM/genpd notifier failure, hardware solver mode, next-wakeup programming, IRQ storm handling, and child population failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-rsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh.c

## Purpose

`rpmh.c` is the client-facing Qualcomm RPMh request layer. It provides synchronous, asynchronous, and batched write APIs for active/sleep/wake resource votes, caches sleep/wake values, and flushes cached low-power votes to the RSC driver during PM transitions.

## Important APIs, Types, and Functions

Exported APIs are `rpmh_write_async()`, `rpmh_write()`, `rpmh_write_batch()`, and `rpmh_invalidate()`. Internal state uses `struct cache_req` for per-resource sleep/wake cached values and `struct batch_cache_req` for cached batched requests. Core helpers include `get_rpmh_ctrlr()`, `rpmh_tx_done()`, `cache_rpm_request()`, `__rpmh_write()`, `__fill_rpmh_msg()`, `flush_batch()`, `send_single()`, and `rpmh_flush()`.

## Control Flow

All write APIs build one or more `rpmh_request` objects. Normal writes cache each command; active-only writes are sent immediately to `rpmh_rsc_send_data()`, while sleep/wake writes complete locally and mark the cache dirty. Synchronous active writes wait up to 10 seconds for `rpmh_tx_done()`. Batched active writes send each message and wait for all completions; batched sleep/wake writes cache the full batch for later flush. `rpmh_flush()` is called with interrupts disabled from RSC PM paths, invalidates stale TCSes if dirty, writes cached batches, emits changed sleep/wake pairs, clears dirty, and updates next wakeup.

## State and Persistence Behavior

The RPMh cache persists per controller. A resource is flush-valid only once both sleep and wake values are known and differ. `dirty` tracks whether TCS hardware needs refresh. Batch cache entries persist until `rpmh_invalidate()` frees them. Hardware persistence occurs through `rpmh-rsc.c` programming TCSes.

## Dependencies and Integration Points

It depends on device-parent drvdata pointing to `struct rsc_drv`, RPMh public TCS structures, completions, spinlocks, waitqueues, and `rpmh-rsc.c` internals. Client device drivers call the exported APIs; RSC PM paths call `rpmh_flush()`.

## Risks and Edge Cases

`rpmh_write_async()` allocates with `GFP_ATOMIC` and relies on `rpmh_tx_done()` to free active requests; non-active requests are immediately completed and freed. `rpmh_write_batch()` allocates one combined object and warns that timed-out completions may later signal freed stack/heap completion storage. `__fill_rpmh_msg()` rejects more than `MAX_RPMH_PAYLOAD` but `rpmh_write_batch()` ignores its return while filling each batch. Cache growth is unbounded by resource count except memory. `rpmh_flush()` uses `spin_trylock()` and can return busy during low-power entry.

## Test Signals

Tests should cover async active completion/free, sync timeout, sleep/wake caching and dirty transitions, same value sleep/wake skipping, batch active success and timeout, batch sleep/wake cache flush, invalid payload counts, allocation failures, `rpmh_invalidate()`, and PM flush with lock contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smd-rpm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/smd-rpm.c

## Purpose

`smd-rpm.c` implements the legacy Qualcomm SMD-backed RPM request transport. It sends resource vote messages over an rpmsg endpoint, waits for RPM acknowledgments, and populates RPM child devices.

## Important APIs, Types, and Functions

The exported API is `qcom_rpm_smd_write()`. Runtime state is `struct qcom_smd_rpm`, holding the rpmsg endpoint, device, completion, mutex, and last ACK status. Wire structs are `qcom_rpm_header`, `qcom_rpm_request`, and `qcom_rpm_message`. `qcom_smd_rpm_callback()` parses RPM response stacks and completes pending writes. Probe/remove manage endpoint state and child population.

## Control Flow

Probe allocates state, initializes mutex/completion, stores the rpmsg endpoint, and populates children. `qcom_rpm_smd_write()` builds a request packet under a mutex, assigns a monotonically increasing message id, sends via `rpmsg_send()`, and waits up to five seconds for callback completion. The callback validates service type and length, walks stacked messages, translates `err` messages to `-ENXIO` for "resource does not exist" or `-EINVAL`, stores status, and completes the waiter.

## State and Persistence Behavior

The driver keeps volatile endpoint state and a global static message id. RPM firmware applies resource votes persistently according to active/sleep flags until overwritten or reset. There is no local cache of votes in this file.

## Dependencies and Integration Points

It depends on rpmsg/SMD, OF child population, platform children, completion/mutex primitives, and public `<linux/soc/qcom/smd-rpm.h>`. It supports generic `qcom,smd-rpm`/`qcom,glink-smd-rpm` plus older compatibles for existing DTs.

## Risks and Edge Cases

The single completion and mutex serialize all writes, but the completion is not reinitialized before every send; correctness depends on completion state after previous waits. The static message id is not protected outside the mutex and can wrap. Callback does not match ACK message id to the pending request. Response parsing trusts lengths enough to advance through the buffer; malformed firmware messages can skip oddly. `memcpy_fromio()` is used on rpmsg buffer memory.

## Test Signals

Test packet size limit, rpmsg send failure, timeout, ACK success, RPM error text mapping, malformed short responses, stacked response parsing, message id wrap, child population, and multiple resource clients issuing serialized writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smd-rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smem.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/smem.c

## Purpose

`smem.c` implements the Qualcomm Shared Memory Manager. It maps SMEM reserved memory, validates global or partitioned heap formats, exports allocation/lookup/free-space/physical-address helpers, exposes SoC id and feature code from SMEM socinfo, and registers a `qcom-socinfo` child device.

## Important APIs, Types, and Functions

Exported APIs include `qcom_smem_alloc()`, `qcom_smem_get()`, `qcom_smem_get_free_space()`, `qcom_smem_virt_to_phys()`, `qcom_smem_get_soc_id()`, `qcom_smem_get_feature_code()`, `qcom_smem_is_available()`, and `qcom_smem_bust_hwspin_lock_by_host()`. The file defines firmware layouts for global TOC entries, partition tables, partition headers, private entries, SMEM info, and regions. Runtime state is the singleton `struct qcom_smem *__smem`.

## Control Flow

Probe resolves the primary reserved memory or `memory-region`, optional RPM MSG RAM, maps the header and partition table, validates SBL initialization, acquires the hwspinlock, computes global heap size, determines SMEM version, remaps either global heap or global partition, enumerates private partitions for APPS, sets `__smem`, and registers socinfo. Allocation takes the hwspinlock, rejects bootloader-fixed items, chooses a private partition, global partition, or legacy global heap, creates an entry, orders writes with `wmb()`, and releases the lock. Lookup walks the selected heap without taking the lock, validating canaries and bounds.

## State and Persistence Behavior

SMEM items are shared-memory allocations visible to multiple processors and persist until reboot. The allocator is append-only; items are not freed. `__smem` is process-global and transitions from `-EPROBE_DEFER` to a live pointer or `-ENODEV`. Partition metadata, free offsets, and TOC entries are persistent shared-memory state and must remain consistent for remote firmware.

## Dependencies and Integration Points

Dependencies include reserved-memory/OF resources, write-combine IO mapping, hwspinlock, platform devices, Qualcomm socinfo, and public SMEM headers. Major consumers include `smp2p.c`, `qcom_stats.c`, remoteproc drivers, socinfo, and many Qualcomm subsystem drivers.

## Risks and Edge Cases

Readers do not take the hwspinlock, so allocation write ordering is critical. `qcom_smem_bust_hwspin_lock_by_host()` dereferences `__smem` without checking `IS_ERR()`. Partition mapping uses 32-bit `phys_addr` in some helpers despite `phys_addr_t` regions. Legacy/global and partition formats have many bounds checks, but malformed firmware tables can still produce invalid mappings or duplicate hosts. `qcom_smem_virt_to_phys()` assumes `__smem` is live. The allocator never reclaims memory.

## Test Signals

Test uninitialized SBL header, unsupported SMEM versions, missing hwspinlock, partition magic/version/size/host failures, duplicate partitions, global partition item count, allocation existing/full/fixed-item cases, private cached and uncached lookup, aux region lookup, free-space sanity, socinfo id/feature code, hwspinlock bust, and early consumers receiving `-EPROBE_DEFER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smem_state.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/smem_state.c

## Purpose

`smem_state.c` provides a small registry for named Qualcomm SMEM-backed state providers. Clients look up state handles from DT phandles and update bit masks through provider callbacks. SMP2P registers outbound entries through this API.

## Important APIs, Types, and Functions

Exported APIs are `qcom_smem_state_update_bits()`, `qcom_smem_state_get()`, `qcom_smem_state_put()`, `devm_qcom_smem_state_get()`, `qcom_smem_state_register()`, and `qcom_smem_state_unregister()`. `struct qcom_smem_state` stores kref, orphan flag, registry list node, OF node, provider private pointer, and ops.

## Control Flow

Providers call `qcom_smem_state_register()` with an OF node, ops, and private data; the state is inserted into a global list. Clients call `qcom_smem_state_get()`, optionally resolving a named index, parse `qcom,smem-states` with one bit argument, and search the registry by OF node. `update_bits()` rejects orphaned states and dispatches to provider ops. `put()` decrements the kref under the list mutex; unregister marks the state orphaned and drops the provider reference.

## State and Persistence Behavior

Registry state is in-memory only. The state value itself lives in the provider, commonly an SMP2P SMEM word. Handles can outlive provider unregister only until their kref is put; `orphan` prevents further updates.

## Dependencies and Integration Points

It depends on OF phandle parsing, device resources, lists, mutexes, krefs, and `<linux/soc/qcom/smem_state.h>`. SMP2P is the primary provider in this subset, while remoteproc/subsystem clients are typical consumers.

## Risks and Edge Cases

`qcom_smem_state_unregister()` sets `orphan` without holding `list_lock`, while `qcom_smem_state_update_bits()` reads it locklessly. `qcom_smem_state_update_bits()` does not take a reference, so callers must hold a valid handle. A missing provider returns `-EPROBE_DEFER`, which can defer clients indefinitely if DT references are wrong. The devm wrapper allocates devres before lookup and frees it on failure.

## Test Signals

Test provider/client probe ordering, named and unnamed lookups, invalid cell counts, missing names, unregister while clients hold references, update after orphan returns `-ENXIO`, missing update op returns `-ENOTSUPP`, and devm cleanup on client removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smem_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smp2p.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/smp2p.c

## Purpose

`smp2p.c` implements Qualcomm Shared Memory Point-to-Point communication. It exposes inbound SMEM bits as nested interrupts and outbound SMEM bits as `qcom_smem_state` providers, using mailbox or syscon IPC kicks to notify the remote processor.

## Important APIs, Types, and Functions

Firmware ABI is `struct smp2p_smem_item`, containing magic, version, features, local/remote pids, entry counts, flags, and up to 16 named 32-bit entries. Driver state uses `struct qcom_smp2p` and per-entry `struct smp2p_entry`. Core functions include `qcom_smp2p_alloc_outbound_item()`, `qcom_smp2p_negotiate()`, `qcom_smp2p_start_in()`, `qcom_smp2p_notify_in()`, `qcom_smp2p_intr()`, irqchip operations, `smp2p_update_bits()`, inbound/outbound entry setup, and `smp2p_parse_ipc()`.

## Control Flow

Probe reads SMEM item ids and local/remote pids, requests a mailbox channel or falls back to `qcom,ipc` syscon, allocates/initializes the outbound SMEM item, parses child nodes into inbound interrupt domains or outbound state entries, scans early inbound entries, kicks the remote, requests a threaded IRQ, and configures wake IRQ support. Incoming IRQs acquire the inbound SMEM item if needed, negotiate protocol version/features, detect SSR restart flags, match newly valid entries, compare current values to `last_value`, and invoke nested IRQs for enabled rising/falling bits. Outbound updates read-modify-write the local entry under a spinlock and kick when changed.

## State and Persistence Behavior

SMEM items persist in shared memory and are single-writer/single-reader by design. The driver resets outbound entries during probe and clears `valid_entries` on remove. Inbound `last_value`, valid-entry count, negotiation state, and SSR ack state are volatile. SSR ack toggles an outbound flag bit to acknowledge remote restarts.

## Dependencies and Integration Points

Dependencies include SMEM allocation/get, SMEM state registry, irqdomain/irqchip, threaded IRQs, mailbox framework, syscon regmap fallback, wake IRQ support, and DT child node contracts. Consumers use standard IRQ phandles for inbound bits and `qcom,smem-states` for outbound bits.

## Risks and Edge Cases

`qcom_smp2p_check_ssr()` resets `last_value` for all inbound entries whenever SSR ack is enabled, even before confirming a restart happened, which can suppress edge detection around restart checks. `qcom_smp2p_outbound_entry()` does not check `out->valid_entries` against `SMP2P_MAX_ENTRY`, so too many outbound child nodes can overflow the entry array. Remove and unwind call `mbox_free_channel()` even when fallback syscon mode set `mbox_chan` to NULL. Protocol negotiation depends on remote version initialization and can stall if remote never writes a version.

## Test Signals

Test mailbox and syscon IPC modes, missing DT properties, outbound item already exists, unsupported inbound version, more than 16 entries, inbound entry late allocation, rising/falling interrupt delivery, irqchip line-level reads before allocation, outbound state updates and kicks, SSR restart/ack flow, wake IRQ setup failure, unwind cleanup, and remove clearing `valid_entries`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smp2p.c -->
