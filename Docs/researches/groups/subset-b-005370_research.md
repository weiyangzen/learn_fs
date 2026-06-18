# subset-b-005370 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/llcc-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/llcc-qcom.c

Purpose: implements the Qualcomm Last Level Cache Controller platform driver and exported slice-management API. Most of the file is SoC-specific slice configuration data for many Qualcomm platforms; the executable logic discovers LLCC banks, programs slice attributes into MMIO regmaps, exposes slice descriptors to client drivers, activates/deactivates slices with refcounting, and optionally registers the LLCC EDAC child device.

Important APIs/types/functions: `struct llcc_slice_config` is the per-slice hardware contract: usecase id, slice id, capacity, priority, reserved/bonus ways, fixed sizing, TCM/cache mode, probe policy, write cache flags, algorithm tuning bits, retention behavior, optional activate-on-init, and parent slice id for grouped v6 slices. `struct qcom_llcc_config` binds a slice table to register offsets, EDAC offsets, bank count overrides, max-capacity shift quirks, and flags such as `skip_llcc_cfg`, `no_edac`, `irq_configured`, and `no_broadcast_register`. Exported API functions are `llcc_slice_getd()`, `llcc_slice_putd()`, `llcc_slice_activate()`, `llcc_slice_deactivate()`, `llcc_get_slice_id()`, and `llcc_get_slice_size()`. Internal programming paths are `_qcom_llcc_cfg_program()` for older layouts, `_qcom_llcc_cfg_program_v6()` for v6 layouts, `qcom_llcc_cfg_program()`, `qcom_llcc_get_cfg_index()`, `qcom_llcc_init_mmio()`, `qcom_llcc_probe()`, and `qcom_llcc_remove()`.

Control flow: probe refuses a second global instance, allocates `drv_data`, maps bank 0, selects a `qcom_sct_config` from the OF match table, optionally selects a DDR-channel-specific configuration through the `multi-chan-ddr` nvmem cell, discovers or overrides the number of banks, maps all per-bank regmaps plus the broadcast register window, reads the LLCC hardware version, optionally maps the broadcast-AND register window for version 4.1+, builds the public descriptor array, stores global driver data, programs every slice, reads an optional ECC IRQ, and registers a `qcom_llcc_edac` platform child unless disabled. Slice activation obtains a descriptor by usecase, serializes on `drv_data->lock`, uses a refcount to avoid redundant hardware transitions, and calls `llcc_update_act_ctrl()` to write trigger bits and poll activation/deactivation status.

State and persistence: runtime state is centralized in the global `drv_data` pointer, initialized to `-EPROBE_DEFER`, set to the active `llcc_drv_data` on probe, and reset to `-ENODEV` on remove or probe failure. Per-slice state is a descriptor array with `slice_id`, `slice_size`, and a `refcount`; hardware state persists in LLCC slice attribute registers, activation state registers, cache allocation/retention algorithm registers, and EDAC register offsets consumed by the child EDAC driver. The many static slice tables are firmware/DT-independent built-in policy for supported SoCs.

Dependencies and integration: integrates with platform/OF matching, nvmem, regmap MMIO, Qualcomm public LLCC headers, EDAC child registration, and consumers that request LLCC slices by `LLCC_*` usecase ids. Hardware assumptions vary by version: older devices use ATTR0/ATTR1/ATTR2 fixed offsets, v6 uses offset tables and 64-byte stride attributes, some platforms lack a broadcast register, and SDM670/SDM845 skip specific non-secure LLCC configuration registers.

Risks and test signals: risks are mostly hardware-contract errors: wrong SoC table data, wrong bank count, incorrect capacity division by bank count, v6 slice grouping mistakes, polling timeouts in activation/deactivation, global singleton lifetime races, and accidental EDAC probing on platforms whose bootloader locks EDAC registers. Test signals include successful probe across DT compatibles, `multi-chan-ddr` config selection, slice get/activate/deactivate refcount behavior under multiple clients, no EDAC child where `.no_edac` is set, EDAC child creation otherwise, and register programming traces or hardware smoke tests on v1/v2.1/v6 LLCC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/llcc-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/mdt_loader.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/mdt_loader.c

Purpose: parses Qualcomm MDT firmware images, extracts metadata for SCM/PAS authentication, computes load size, and loads split or monolithic ELF32 program segments into a caller-provided memory region for remote processors.

Important APIs/types/functions: exported helpers are `qcom_mdt_get_size()`, `qcom_mdt_read_metadata()`, `qcom_mdt_load_no_init()`, `qcom_mdt_load()`, and `qcom_mdt_pas_load()`. Internal helpers are `mdt_header_valid()`, `mdt_phdr_loadable()`, `mdt_load_split_segment()`, `__qcom_mdt_pas_init()`, and `qcom_mdt_bins_are_split()`. The code uses ELF32 headers/program headers, Qualcomm MDT segment flag masks such as `QCOM_MDT_TYPE_HASH` and `QCOM_MDT_RELOCATABLE`, and SCM PAS APIs including `qcom_scm_pas_init_image()` and `qcom_scm_pas_mem_setup()`.

Control flow: all public paths first validate the firmware as an ELF32 MDT with bounded program and section tables. Size calculation walks loadable non-hash PT_LOAD segments and returns the aligned span between the lowest and highest physical addresses. Metadata extraction requires an ELF header segment and a hash segment, allocates a contiguous metadata buffer, copies the ELF header, then copies the hash either from the same firmware blob or from a split `*.bNN` segment file. PAS load paths authenticate metadata first, optionally set up relocation memory through SCM if any segment is relocatable, then call `qcom_mdt_load_no_init()` to copy each loadable segment into the target memory area and zero BSS tails.

State and persistence: this file keeps no persistent driver state. It consumes immutable `struct firmware` blobs and writes into caller-owned memory. It returns a relocation base through `reloc_base` when requested. Persistent effects occur outside the file through SCM/PAS image initialization and memory setup, and through firmware files requested from the kernel firmware loader.

Dependencies and integration: used by Qualcomm remoteproc and PAS clients that allocate a carveout, request an MDT firmware, authenticate it, and then load its segments. It depends on Linux firmware loading, ELF definitions, overflow-safe size helpers, SCM PAS context state, and the naming convention that split segment files replace the last three characters of the MDT filename with `b%02d`.

Risks and test signals: malformed firmware can exercise integer overflow, truncated segment, `p_filesz > p_memsz`, bad relocation, and missing hash-segment paths. The split-file naming logic rejects names shorter than four bytes and assumes standard `.mdt` style naming. Test signals include load-size results for relocatable and fixed-address images, monolithic vs split image loading, metadata extraction where the hash is packed after the ELF header or stored past the MDT file, SCM authentication failures, memory-range rejection, and zero-fill validation for segments with `p_memsz > p_filesz`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/mdt_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ocmem.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/ocmem.c

Purpose: provides an allocator and hardware programming driver for legacy Qualcomm On Chip Memory blocks used by clients such as graphics on some Snapdragon SoCs. It exposes a small client API to obtain an OCMEM provider from DT and allocate/free aligned memory from the SRAM-like region while programming macro power and protection state.

Important APIs/types/functions: `struct ocmem` stores device, config, memory resource, MMIO base, clocks, hardware profile, region array, and active allocation bitmap. `struct ocmem_region` tracks interleaving mode, region mode, macro count, macro states, and sizes. Exported functions are `of_get_ocmem()`, `ocmem_allocate()`, and `ocmem_free()`. Internal helpers include `update_ocmem()`, `phys_to_offset()`, `device_address()`, `update_range()`, and platform probe/remove functions. Supported configs are `qcom,msm8226-ocmem` and `qcom,msm8974-ocmem`.

Control flow: probe waits for SCM availability, allocates state, obtains optional core/interface clocks, maps the control MMIO resource, stores the memory resource, enables clocks, optionally restores secure configuration, reads hardware version/profile registers, computes ports/macros/interleaving and region sizes, initializes each region and macro as clock-off, then publishes `platform_set_drvdata()`. A client calls `of_get_ocmem()` through an `sram` phandle. `ocmem_allocate()` currently accepts only `OCMEM_GRAPHICS`, validates 64 KiB minimum/alignment, atomically reserves the client allocation bit, creates a buffer covering offset zero, powers the range to `CORE_ON`, and either calls SCM OCMEM lock or programs the graphics MPU registers. `ocmem_free()` reverses macro state, unlocks or clears MPU registers, frees the buffer, and clears the active bit.

State and persistence: persistent hardware state includes region mode control, macro power-gating state, and graphics MPU start/end registers or SCM lock state. Runtime state is the region/macro model and `active_allocations` bitset; allocation is deliberately single-client per `enum ocmem_client` and currently single-range at offset zero. No persistent software storage is maintained.

Dependencies and integration: depends on platform resources named `ctrl` and `mem`, optional clocks named `core` and `iface`, DT `sram` phandles from clients, Qualcomm SCM calls for secure config and OCMEM lock/unlock when available, and public `<soc/qcom/ocmem.h>` client types. It is integrated as a platform driver rather than a generic genalloc SRAM provider.

Risks and test signals: only graphics is supported; any other client warns and fails. Allocation does not search free space, so size and multi-client behavior are intentionally constrained. `phys_to_offset()` returns zero for out-of-range addresses, which would be ambiguous if reused beyond the current fixed offset. Failure after `update_range()` but before SCM lock does not restore macro state. Test signals include probe deferral until SCM, clock enable/disable balance, valid `sram` phandle lookup, 64 KiB alignment rejection, duplicate allocation returning `-EBUSY`, secure and non-secure lock paths, and register state after free/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ocmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_interface.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_interface.c

Purpose: implements Qualcomm Protection Domain Restart helper APIs. It lets client drivers discover a service domain through SERVREG locator QMI, subscribe to state changes through SERVREG notifier QMI, receive serialized up/down callbacks, acknowledge state indications after client cleanup, and request a PD restart.

Important APIs/types/functions: `struct pdr_handle` owns two `qmi_handle`s, lookup and indication lists, mutexes, work items, workqueues, and the client status callback. `struct pdr_service` represents one tracked service path with service id/instance, QRTR address, lookup/register flags, connection state, and current SERVREG state. Exported functions are `pdr_handle_alloc()`, `pdr_handle_release()`, `pdr_add_lookup()`, and `pdr_restart_pd()`. Internal control points include locator QMI ops, notifier QMI ops, `pdr_register_listener()`, `pdr_notifier_work()`, `pdr_indication_cb()`, `pdr_indack_work()`, `pdr_get_domain_list()`, `pdr_locate_service()`, and `pdr_locator_work()`.

Control flow: allocation initializes lists, locks, work items, workqueues, a locator QMI handle that looks up `QMI_SERVICE_ID_SERVREG_LOC`, and a notifier QMI handle with an indication handler. `pdr_add_lookup()` validates names, rejects duplicate service paths, records a pending lookup, and schedules locator work. When the locator server appears, locator work queries the domain list in offset chunks until it finds the requested service path and then adds a notifier lookup for the discovered instance. When the notifier server appears, notifier work registers a listener and calls the client status callback with the current state. Indications are queued to an ordered high-priority workqueue, the callback is invoked under `status_lock`, then an ACK is sent so the remote side can continue restart handling. `pdr_restart_pd()` validates that the service is still tracked and connected, sends SERVREG restart, and maps disabled/remote errors to Linux errno values.

State and persistence: runtime state is in the tracked lookup list, pending indication-ack list, QRTR locator address, service addresses, and boolean work flags. There is no disk persistence. Remote SERVREG state is mirrored in each `pdr_service->state`, and the acknowledgement sequence is stateful because ACKs are delayed until after client notification.

Dependencies and integration: depends on QRTR/QMI infrastructure, SERVREG QMI element-info tables declared in `pdr_internal.h`, workqueues, mutexes, and public `<linux/soc/qcom/pdr.h>`. PMIC GLINK and other Qualcomm subsystem clients use it to tie rpmsg/channel availability to protection-domain lifecycle.

Risks and test signals: workqueue and list lifetime are the key risks. `pdr_handle_release()` deletes lookups before cancelling work, so queued indication nodes can still hold `pds` pointers if indications raced with release; test teardown paths should stress this. `pdr_notify_lookup_failure()` is called while locator work holds `list_lock` and itself deletes from the list; this works only because it does not take `list_lock`. Lookup failures with `-ENXIO` intentionally leave the service pending. Test signals include locator delayed startup, duplicate lookup rejection, paged domain-list responses, notifier connect/disconnect, indication ACK ordering, restart disabled mapping to `-EOPNOTSUPP`, and release during active indications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_internal.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_internal.h

Purpose: defines the internal SERVREG QMI message ABI used by `pdr_interface.c`. It is not a standalone implementation file; it supplies message ids, maximum encoded lengths, request/response structures, indication structures, and external QMI element-info declarations.

Important APIs/types/functions: constants cover SERVREG operations for register listener, get domain list, state update indication, set ACK, restart PD, and local PFR. Structures include `servreg_location_entry`, `servreg_get_domain_list_req`, `servreg_get_domain_list_resp`, `servreg_register_listener_req`, `servreg_register_listener_resp`, `servreg_restart_pd_req`, `servreg_restart_pd_resp`, `servreg_state_updated_ind`, `servreg_set_ack_req`, `servreg_set_ack_resp`, `servreg_loc_pfr_req`, and `servreg_loc_pfr_resp`. The header declares QMI element-info arrays such as `servreg_get_domain_list_req_ei[]` and `servreg_state_updated_ind_ei[]`.

Control flow: there is no runtime flow in the header. The structures define the payloads for the PDR flow: locator domain-list requests/responses, notifier listener registration, async state indications, indication ACK requests, and restart requests.

State and persistence: the structures carry transient QMI state only: service names/paths, domain offsets, domain records, current state, transaction ids, service-data fields, and QMI response codes. There is no local persistence.

Dependencies and integration: includes public PDR definitions from `<linux/soc/qcom/pdr.h>` for `SERVREG_NAME_LENGTH`, `SERVREG_PFR_LENGTH`, and service state types. It also assumes QMI core types such as `struct qmi_response_type_v01` and `struct qmi_elem_info` are available through that include chain. Element-info definitions are expected elsewhere in the same driver build.

Risks and test signals: the risk is ABI mismatch: wrong max lengths, field widths, enum encoding, or string sizes will make QMI transactions fail or silently decode wrong service paths/states. Test signals are successful domain-list pagination, listener registration response decoding, state indication decoding with transaction id, ACK request encoding, and restart response error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_glink.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_glink.c

Purpose: implements the core Qualcomm PMIC GLINK platform and rpmsg bridge. It owns the shared rpmsg endpoint, exposes a small client registration/send API, creates auxiliary devices for battery/power-supply, USB-C altmode, and UCSI subdrivers, and maps PDR/rpmsg availability into client state notifications.

Important APIs/types/functions: `struct pmic_glink` stores the device, PDR handle, rpmsg endpoint, SoC data, auxiliary devices, state locks, client list, and state flags. `struct pmic_glink_client` records owner id, callbacks, PDR callback, and private data. Exported functions are `devm_pmic_glink_client_alloc()`, `pmic_glink_client_register()`, and `pmic_glink_send()`. Key internal functions include `pmic_glink_rpmsg_callback()`, `pmic_glink_state_notify_clients()`, `pmic_glink_pdr_callback()`, `pmic_glink_rpmsg_probe()`, `pmic_glink_rpmsg_remove()`, `pmic_glink_probe()`, and `pmic_glink_remove()`.

Control flow: module init registers the platform driver, then the rpmsg driver. Platform probe allocates state, initializes locks/list, selects SoC data, allocates a PDR handle, creates auxiliary devices based on a client mask, optionally registers a charger PD lookup, and publishes the singleton `__pmic_glink`. The rpmsg probe finds that singleton, stores the endpoint, determines whether PDR is expected for the channel, sets PDR state up on channels without PDR, and notifies clients if the combined endpoint/PDR state is usable. Incoming rpmsg packets are demultiplexed by GLINK header owner id to registered clients. Sends serialize through `state_lock` and retry `rpmsg_send()` on `-EAGAIN` until a 5-second timeout.

State and persistence: runtime state is the singleton pointer, endpoint pointer, client list, `pdr_state`, `client_state`, and `pdr_available`. There is no persistent storage. Client state is derived from both PDR state and rpmsg endpoint availability: clients see UP only when the PD is up and the endpoint exists, and DOWN if either disappears.

Dependencies and integration: depends on auxiliary bus, rpmsg IDs `PMIC_RTR_ADSP_APPS` and `PMIC_RTR_SOCCP_APPS`, PDR helper APIs, Qualcomm PMIC GLINK public headers, platform OF compatibles `qcom,pmic-glink`, `qcom,glymur-pmic-glink`, and `qcom,kaanapali-pmic-glink`, and child drivers that bind to `pmic_glink.altmode`, `pmic_glink.ucsi`, and `pmic_glink.power-supply`.

Risks and test signals: callbacks are invoked while holding `client_lock` spinlock, so child callbacks must not sleep; this is a critical integration constraint. Singleton coupling means rpmsg probe order and platform probe/remove ordering must be tested. `pmic_glink_remove()` releases PDR before deleting auxiliary devices, so child teardown should tolerate state callbacks ending first. Test signals include platform-before-rpmsg and rpmsg-before-platform ordering, ADSP PDR transitions, SOCCP no-PDR channel behavior, owner-id demux to multiple clients, send timeout on a congested endpoint, and auxiliary-device add/remove unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_glink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_glink_altmode.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_glink_altmode.c

Purpose: implements the PMIC GLINK USB-C alternate-mode auxiliary driver. It decodes PMIC GLINK USBC notifications into Type-C orientation switch, mux, retimer, DisplayPort HPD bridge, Thunderbolt, USB4, and safe/USB states, and acknowledges PMIC notifications after applying local state.

Important APIs/types/functions: message structures are `usbc_write_req`, `usbc_notify`, and the SC8180X packed notification variant. `struct pmic_glink_altmode` owns the GLINK client, owner id, PAN ACK completion, request mutex, enable work, and up to three ports. `struct pmic_glink_altmode_port` owns Type-C switch/mux/retimer handles, DP/TBT altmode descriptors, HPD bridge, cached notification fields, and work item. Core functions include `pmic_glink_altmode_request()`, state appliers for DP/TBT/USB4/USB/safe, `pmic_glink_altmode_worker()`, SC8180X and SC8280XP notification decoders, `pmic_glink_altmode_callback()`, `pmic_glink_altmode_pdr_notify()`, and `pmic_glink_altmode_probe()`.

Control flow: probe allocates state, selects the PMIC GLINK owner id with an SC8180X quirk, initializes the ACK completion and lock, iterates child connector nodes by `reg`, allocates an HPD bridge per valid port, prepares DP and TBT altmode descriptors, obtains Type-C mux/retimer/orientation switch handles with devm cleanup actions, adds HPD bridges, allocates a PMIC GLINK client, and registers it. When PDR state becomes UP, enable work sends `ALTMODE_PAN_EN`. Incoming GLINK callbacks either complete a write request ACK or decode a notification. Decoded notification state is cached in the relevant port and scheduled to port work; the worker sets orientation, applies DP/TBT/USB4/USB/safe mux and retimer state, notifies the DP HPD bridge for DP, and sends `ALTMODE_PAN_ACK` for that port.

State and persistence: per-port cached state includes orientation, SVID, mux control, mode/pin assignment, DP HPD state/IRQ, and TBT/USB4 cable data. The driver maintains no persistent storage, but it does maintain an in-flight request synchronization state through a mutex plus a single shared completion because PMIC WRITE_REQ ACKs do not identify the original request.

Dependencies and integration: depends on PMIC GLINK client APIs, PDR service states, USB PD/Type-C altmode constants, Type-C mux/switch/retimer provider drivers, DRM DP AUX HPD bridge helpers, auxiliary bus binding, and child connector firmware nodes. It accepts both older SC8180X packed notifications and newer SC8280XP-style structured notifications with SVID encoded in the opcode high bits.

Risks and test signals: `pmic_glink_altmode_request()` uses one shared completion and does not reinitialize it before each send, so a stale completion would make later requests look immediately acknowledged; tests should verify repeated enable and per-port ACK sequences. Probe creates work items but has no explicit remove/cancel path, relying on devm/module teardown, so in-flight work during detach is a lifecycle risk. DP pin assignment subtracts `DPAM_HPD_A` and assumes firmware-provided values are valid. Test signals include all mux states, DP HPD connect/disconnect/IRQ notifications, TBT and USB4 cable speed fallback paths, invalid port and invalid length warnings, SC8180X quirk owner id, PDR up notification enabling, and ACK timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_glink_altmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.c

Purpose: debugging rpmsg driver that periodically requests PMIC ChargerPD ulog text and emits each log line through a tracepoint. It is intentionally not auto-loaded through a module device table.

Important APIs/types/functions: `struct pmic_pdcharger_ulog` holds the rpmsg device and delayed work. `struct pmic_pdcharger_ulog_hdr`, `get_ulog_req_msg`, and `get_ulog_resp_msg` define the GLINK/rpmsg message format. Internal functions are `pmic_pdcharger_ulog_write_async()`, `pmic_pdcharger_ulog_request()`, `pmic_pdcharger_ulog_work()`, `pmic_pdcharger_ulog_handle_message()`, `pmic_pdcharger_ulog_rpmsg_callback()`, probe, and remove. `CREATE_TRACE_POINTS` includes `pmic_pdcharger_ulog.h` to instantiate `trace_pmic_pdcharger_ulog_msg()`.

Control flow: rpmsg probe allocates state, initializes delayed work, stores drvdata, and immediately sends a `GET_CHG_ULOG_REQ` with `MAX_ULOG_SIZE`. The rpmsg callback reads the opcode; for `GET_CHG_ULOG_REQ` responses it schedules the next request after one second and parses the response buffer into newline-separated trace messages. Remove cancels delayed work. Unknown opcodes are logged as errors.

State and persistence: the only runtime state is the rpmsg pointer and delayed polling work. Firmware log contents are transient; the driver does not store them, exposing them only as trace events. The response buffer is forcibly NUL-terminated at `MAX_ULOG_SIZE - 1` before line splitting.

Dependencies and integration: depends on rpmsg channel `PMIC_LOGS_ADSP_APPS`, Linux tracepoint infrastructure, and the local trace header. It includes PDR and debugfs headers but does not use them directly. Lack of `MODULE_DEVICE_TABLE` is intentional so users load it manually for debugging.

Risks and test signals: `pmic_pdcharger_ulog_rpmsg_callback()` dereferences the message header without checking `len >= sizeof(*hdr)`, so truncated rpmsg packets can read beyond the provided buffer. Request messages assign `log_size` without endian conversion while the header uses little-endian fields; this should match firmware expectations or be corrected. `pmic_pdcharger_ulog_request()` return value is ignored on probe. Test signals include manual module load, initial request success, one-second polling cadence, full 8192-byte response parsing, newline tokenization into trace events, remove cancellation, unknown opcode handling, and truncated packet robustness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.h

Purpose: tracepoint definition header for the PMIC ChargerPD ulog debug driver. It defines the `pmic_pdcharger_ulog_msg` event that carries one parsed firmware log line.

Important APIs/types/functions: the sole trace event is `TRACE_EVENT(pmic_pdcharger_ulog_msg, TP_PROTO(char *msg), TP_ARGS(msg), TP_STRUCT__entry(__string(msg, msg)), TP_fast_assign(__assign_str(msg)), TP_printk("%s", __get_str(msg)))`. The header also sets `TRACE_SYSTEM`, `TRACE_INCLUDE_PATH`, and `TRACE_INCLUDE_FILE` and includes `<trace/define_trace.h>` outside the include guard as required by Linux tracepoint conventions.

Control flow: there is no normal function flow. When included with `CREATE_TRACE_POINTS` in `pmic_pdcharger_ulog.c`, this header creates the tracepoint definition; other inclusions would provide declarations.

State and persistence: tracepoint instances copy the string into the trace ring buffer via `__string`/`__assign_str`. Persistence is limited to the kernel tracing buffer configured by the user.

Dependencies and integration: depends on Linux tracepoint infrastructure and the `.c` file's `CREATE_TRACE_POINTS` include pattern. The event name is consumed by ftrace/perf/trace-cmd users who enable `pmic_pdcharger_ulog:pmic_pdcharger_ulog_msg`.

Risks and test signals: trace headers are sensitive to include guard and `TRACE_INCLUDE_*` correctness; wrong values break trace generation or module build. Test signals are successful module build, presence of the event under tracing events, and emitted log lines matching tokens parsed by `pmic_pdcharger_ulog_handle_message()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-geni-se.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-geni-se.c

Purpose: implements the Qualcomm GENI Serial Engine wrapper driver and common exported helpers used by protocol drivers such as UART, SPI, I2C, and I3C. It manages QUP wrapper resources, serial-engine initialization, FIFO/DMA/GPI transfer-mode setup, packing rules, clocks, interconnect paths, DMA buffer mapping, and optional serial-engine firmware loading.

Important APIs/types/functions: `struct geni_wrapper` represents a QUP wrapper with MMIO base and AHB clocks; `struct geni_se_desc` describes wrapper clock names; `struct se_fw_hdr` describes protocol firmware embedded in an ELF segment. Exported helpers include `geni_se_get_qup_hw_version()`, `geni_se_init()`, `geni_se_select_mode()`, `geni_se_config_packing()`, `geni_se_resources_on()`, `geni_se_resources_off()`, `geni_se_clk_tbl_get()`, `geni_se_clk_freq_match()`, TX/RX DMA init/prep/unprep helpers, `geni_icc_get()`, `geni_icc_set_bw()`, `geni_icc_set_tag()`, `geni_icc_enable()`, `geni_icc_disable()`, and `geni_load_se_firmware()`. Internal firmware helpers include `geni_find_protocol_fw()`, `geni_configure_xfer_mode()`, `geni_enable_interrupts()`, `geni_write_fw_revision()`, and `geni_load_se_fw()`.

Control flow: wrapper probe maps QUP MMIO, obtains wrapper clocks based on compatible data, stores `geni_wrapper` as drvdata, and populates child serial-engine devices. Protocol drivers bind to children and use exported helpers: resources are turned on by enabling wrapper and SE clocks and selecting default pinctrl, then `geni_se_init()` clears IRQs, enables CGC, sets IO mode, watermarks, and common IRQs. Transfer-mode selection clears IRQs and programs FIFO, DMA, or GPI event/IRQ paths. DMA prep maps caller buffers on the wrapper device and writes DMA pointer/length registers. Firmware loading reads a wrapper `firmware-name` property, requests the firmware, finds a protocol-specific SEFW segment, votes interconnect bandwidth, enables ICC and clocks, configures wrapper and SE CGC, writes config registers and firmware RAM, records revision, sets transfer mode, enables DMA interface, and disables resources/ICC on exit.

State and persistence: runtime state lives mostly in caller-owned `struct geni_se`: wrapper pointer, base, clocks, clock performance table, interconnect paths, and bandwidth/tag values. The wrapper driver holds MMIO/clocks and child population state. Hardware state persists in QUP common registers, SE CGC/IRQ/mode registers, packing registers, DMA pointer/length registers, firmware RAM/config registers, and firmware revision registers. Software persists a generated clock table in devm memory after first `geni_se_clk_tbl_get()`.

Dependencies and integration: depends on platform/OF/ACPI probing, clk framework, pinctrl PM states, DMA mapping, interconnect framework, firmware loader, ELF32 parsing, and public `<linux/soc/qcom/geni-se.h>` definitions. It integrates as common infrastructure for multiple serial protocol drivers; those drivers choose clocks, ICC bandwidth, packing, transfer mode, and DMA usage.

Risks and test signals: firmware parsing lacks the full `mdt_header_valid()` style program-header bounds validation before computing `phdrs`, so corrupt firmware with bad `e_phoff` is a risk. `geni_find_protocol_fw()` modifies `sefw->fw_size_in_items` in the firmware buffer when odd, which assumes the firmware data is writable. ICC enable failure after partially enabling earlier paths does not unwind already-enabled paths. ACPI paths skip resource on/off work, so protocol drivers must account for that. Test signals include child population for all compatibles, clock-count validation, FIFO/DMA/GPI mode register state, packing output for common bit widths, DMA map/unmap error paths, ICC bandwidth votes, firmware-name deferral on missing firmware, protocol mismatch rejection, truncated firmware rejection, and UART forced FIFO mode despite `qcom,enable-gsi-dma`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-geni-se.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-pbs.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-pbs.c

Purpose: provides a small Qualcomm PMIC PBS client driver API. It lets consumers find a PBS device through DT and trigger PMIC PBS RAM sequences by setting scratch bits, issuing a software trigger, and waiting for acknowledgement bits.

Important APIs/types/functions: `struct pbs_dev` holds device, parent regmap, mutex, optional consumer device link, and base offset. Exported functions are `qcom_pbs_trigger_event()` and `get_pbs_client_device()`. Internal `qcom_pbs_wait_for_ack()` polls `PBS_CLIENT_SCRATCH2` for a bit or error value. Probe reads the parent SPMI regmap and the child `reg` base address.

Control flow: a consumer calls `get_pbs_client_device()`, which parses `qcom,pbs`, finds the platform device, retrieves drvdata, creates an autoremove supplier device link, and returns the PBS handle. To trigger events, `qcom_pbs_trigger_event()` validates a nonzero bitmap, serializes on `pbs->lock`, clears a stale `0xff` error in `SCRATCH2`, then for each requested bit clears the ACK bit, sets the corresponding `SCRATCH1` bit, sets the software trigger bit in `TRIG_CTL`, polls for ACK/NACK, clears scratch bits, and finally clears all requested `SCRATCH1` bits.

State and persistence: runtime state is minimal: base register offset, regmap, lock, and the most recent device link pointer. Hardware scratch registers carry transient request/ack/error state. No persistent storage is maintained.

Dependencies and integration: depends on OF phandles, platform devices, parent PMIC regmap, SPMI-style child layout, device links, and public `<linux/soc/qcom/qcom-pbs.h>`. Consumer drivers are responsible for defining the PBS phandle and using bitmaps agreed with PMIC PBS firmware.

Risks and test signals: if multiple consumers call `get_pbs_client_device()`, the single `pbs->link` field is overwritten, although links are autoremove supplier links; this is mostly a bookkeeping risk. `qcom_pbs_wait_for_ack()` treats exactly `0xff` as NACK and otherwise any requested bit as success, so mixed error/ack values need firmware validation. Cleanup ignores errors from final scratch clears. Test signals include missing phandle deferral, parent regmap absence, valid device link creation, multi-bit bitmap ordering, timeout after roughly `DELAY * RETRIES`, NACK clearing, concurrent triggers serialized by the mutex, and correct scratch register cleanup after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom-pbs.c -->
