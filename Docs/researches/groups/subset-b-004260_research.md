# Research: subset-b-004260

Work item `subset-b-004260` covers Intel MEI host bus protocol, hardware backends, userspace character-device entry points, tracing, and the MEI HDCP client bridge under `sources/distributed-fs/ceph-client/drivers/misc/mei`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.c

Purpose: implements the MEI Host Bus Message protocol state machine. It negotiates the HBM version with firmware, configures optional capabilities, enumerates firmware clients, handles dynamic client add/remove style messages, and translates connect, disconnect, notification, flow-control, DMA, and power-gating HBM packets into `struct mei_device` and `struct mei_cl` state.

Important APIs and functions: exported entry points include `mei_hbm_start_req()`, `mei_hbm_start_wait()`, `mei_hbm_dispatch()`, `mei_hbm_reset()`, `mei_hbm_idle()`, `mei_hbm_cl_connect_req()`, `mei_hbm_cl_disconnect_req()`, `mei_hbm_cl_disconnect_rsp()`, `mei_hbm_cl_flow_control_req()`, `mei_hbm_cl_notify_req()`, `mei_hbm_cl_dma_map_req()`, `mei_hbm_cl_dma_unmap_req()`, `mei_hbm_pg()`, and `mei_hbm_pg_resume()`. Local helpers build common MEI/HBM headers, find clients by host/ME address, map firmware connection status to errno, add enumerated `mei_me_client` objects, and process per-operation responses from `dev->ctrl_rd_list`.

Control flow: `mei_hbm_start_req()` resets HBM bookkeeping, sends `HOST_START_REQ_CMD`, enters `MEI_HBM_STARTING`, arms `init_clients_timer`, and schedules the stall timer. `mei_hbm_dispatch()` is called by the interrupt read path after reading an HBM packet from hardware. Start response chooses the negotiated version, rejects unsupported firmware with `HOST_STOP_REQ_CMD`, configures feature flags, optionally sends capabilities and DMA setup requests, and then sends client enumeration. Enumeration stores `valid_addresses` into `dev->me_clients_map`; property responses add `mei_me_client` entries until no more addresses remain, then set `MEI_HBM_STARTED` and call `mei_host_client_init()`. Client connect/disconnect/notify/DMA responses complete queued control callbacks by updating client state/status and waking waiters.

State and persistence: state is in memory only: `dev->hbm_state`, `dev->version`, HBM feature booleans, firmware-client lists/maps, DMA-ring descriptors, `dev->pg_event`, per-client flow-control credits, notification flags, and pending control callback lists. No disk persistence exists. Reset removes all ME clients and returns HBM to idle.

Dependencies and integration: depends on `mei_dev.h`, `client.h`, HBM wire structures from `hw.h`, core write/read helpers from `mei_device` hardware ops, runtime PM, wait queues, and workqueues. It integrates with interrupt handling through `mei_hbm_dispatch()`, with initialization through `mei_start()`/`mei_reset()`, with runtime PM through `mei_hbm_pg()` and `mei_hbm_pg_resume()`, and with the MEI bus through `mei_host_client_init()` and bus rescan scheduling.

Risks: most failures are protocol/state mismatches that force reset through `-EPROTO` or `-EIO`. `BUG_ON(hdr->length >= sizeof(dev->rd_msg_buf))` relies on prior header validation. Feature negotiation is version-gated and capability-response-gated; mistakes can expose unsupported vtags, GSC headers, DMA rings, or client DMA. Dynamic client add removes existing UUIDs before allocation; allocation failure returns an add response failure but may have already changed the list. Timeouts during HBM start, capability, DMA, enum, or properties reset the link via the stall timer.

Test signals: useful validation includes boot/probe logs for HBM version negotiation, sysfs `hbm_ver`, client enumeration on the MEI bus, successful userspace `IOCTL_MEI_CONNECT_CLIENT`, notification set/get, DMA-ring fallback when firmware rejects DMA setup, runtime PM entry/exit traces, and reset behavior on injected bad HBM states or missing responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.h

Purpose: declares the HBM protocol state enum and the public HBM helpers used by MEI core, interrupt handling, client operations, and hardware power-management code.

Important APIs and types: `enum mei_hbm_state` names the HBM lifecycle: idle, starting, capabilities setup, DMA-ring setup, enum clients, client properties, started, and stopped. The header exposes `mei_hbm_state_str()`, `mei_hbm_dispatch()`, start/reset/idle helpers, client control requests, protocol-version support check, power-gating message helpers, notification request, and client DMA map/unmap request.

Control flow: consumers call `mei_hbm_start_req()` during reset/start, wait with `mei_hbm_start_wait()`, and pass inbound host-bus messages to `mei_hbm_dispatch()` from the read interrupt path. Client operations enqueue callbacks elsewhere and use these request helpers when the write interrupt path has space. Runtime PM invokes `mei_hbm_pg()` for PG entry/exit handshakes and `mei_hbm_pg_resume()` when firmware asks the host to wake.

State and persistence: this header owns no storage; it defines state symbols used in `struct mei_device`. Persistence is volatile and reset-driven.

Dependencies and integration: forward-declares `struct mei_device`, `struct mei_msg_hdr`, `struct mei_cl`, and `struct mei_dma_data`, so it can be included without pulling the full MEI object graph. The implementations depend on HBM command structs in `hw.h`.

Risks: adding an HBM state in the implementation without updating this enum and string conversion would reduce observability and may break state-machine checks. Public prototypes make this a cross-file contract; signature changes require coordinated updates in client, interrupt, and init code.

Test signals: compile coverage from all MEI objects, runtime sysfs `hbm_ver`, and logs that print HBM state names during timeout or mismatch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Kconfig

Purpose: adds the `INTEL_MEI_HDCP` tristate configuration option for the MEI HDCP 2.2 services client.

Important APIs and types: the file defines one Kconfig symbol, `INTEL_MEI_HDCP`, with user-visible text "Intel HDCP2.2 services of ME Interface". It depends on `INTEL_MEI_ME` and on either `DRM_I915`, `DRM_XE`, or `COMPILE_TEST`.

Control flow: this is build-time configuration only. When enabled as built-in or module, the local Makefile builds `mei_hdcp.o`; otherwise the MEI HDCP client driver is omitted.

State and persistence: no runtime state. The selected Kconfig value is persisted in the kernel build configuration.

Dependencies and integration: ties the MEI HDCP module to the MEI ME PCI backend and to Intel display stacks that consume `i915_hdcp_ops`. The `DRM_XE` allowance means the client can be built even though this source still names i915 component interfaces.

Risks: dependency drift can break builds if display component interfaces move. Too-strict dependencies hide the driver on supported platforms; too-loose dependencies cause unresolved symbols or unusable modules.

Test signals: `make oldconfig` visibility, `CONFIG_INTEL_MEI_HDCP=m/y` builds, compile-test coverage without Intel display hardware, and module autoload on systems exposing the HDCP MEI UUID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Makefile

Purpose: builds the MEI HDCP client object when `CONFIG_INTEL_MEI_HDCP` is selected.

Important APIs and types: the single object rule is `obj-$(CONFIG_INTEL_MEI_HDCP) += mei_hdcp.o`.

Control flow: Kbuild includes `mei_hdcp.c` in the kernel or module according to the Kconfig tristate. No custom flags or multi-object composition are used.

State and persistence: no runtime state. Build output is controlled by the kernel configuration.

Dependencies and integration: relies on the surrounding MEI Kbuild hierarchy to descend into `hdcp/` and on Kconfig to ensure required MEI/display symbols are available.

Risks: if `mei_hdcp.c` grows into multiple source files, this Makefile must be updated to use an aggregate object list. Missing directory integration outside this file would silently skip the module even when Kconfig is set.

Test signals: `make M=drivers/misc/mei/hdcp`, full kernel builds with `CONFIG_INTEL_MEI_HDCP=m/y`, and checking that `mei_hdcp.ko` is emitted for modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.c

Purpose: implements the MEI bus client for Intel HDCP 2.2 firmware services. It is a translation layer between the Intel display HDCP component API and ME firmware wire commands carried through `mei_cl_device`.

Important APIs and functions: HDCP operation callbacks include session initiation, receiver certificate verification and Km preparation, H-prime verification, pairing-info storage, locality-check initiation and L-prime validation, session-key retrieval, repeater topology validation/ack preparation, M-prime verification, enabling authentication, and session close. These populate `static const struct i915_hdcp_ops mei_hdcp_ops`. Probe/remove are `mei_hdcp_probe()` and `mei_hdcp_remove()`, with component glue through `mei_component_master_bind()`, `mei_component_master_unbind()`, and `mei_hdcp_component_match()`.

Control flow: each HDCP callback validates pointers, fills a specific `wired_cmd_*_in` structure with `HDCP_API_VERSION`, command ID, success status, buffer length, port identity, and protocol-specific data, sends it with `mei_cldev_send()`, reads the matching output struct with `mei_cldev_recv()`, checks `header.status`, and copies firmware output into DRM HDCP message structures. `mei_hdcp_probe()` enables the MEI client, allocates an `i915_hdcp_arbiter`, installs component match data, and registers as a component master. Bind exposes `mei_hdcp_ops` and this MEI device to the Intel display component.

State and persistence: state is per-probe heap memory in `i915_hdcp_arbiter` stored as MEI client driver data. HDCP session state and pairing material are held or generated by ME firmware and passed synchronously; this driver does not persist secrets to disk.

Dependencies and integration: depends on the MEI client bus, Linux component framework, PCI device matching, DRM connector and Intel HDCP interfaces, and command definitions from DRM HDCP headers via `mei_hdcp.h`. The device table matches the HDCP MEI UUID `B638AB7E-94E2-4EA2-A552-D1C54B627F04`.

Risks: all command exchanges are synchronous and assume ordered request/response behavior on the MEI client. Short positive transfers are not explicitly checked against full struct sizes, so transport semantics must guarantee full messages or upper layers may consume partially initialized output. `struct_size()` and `array_size()` protect M-prime variable stream allocation, but correctness depends on `data->k` and `data->streams`. Component matching is topology-sensitive: it requires the Intel VGA device parent and the MEI HDCP grandparent to share the same PCH parent.

Test signals: module probe on systems with HDCP MEI UUID, component bind with i915/xe HDCP subcomponent, HDCP 2.2 authentication over direct and repeater sinks, failure-path checks for firmware status values, runtime unbind/remove, and KASAN/KMSAN coverage around variable stream command allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.h

Purpose: provides the private include guard and pulls in DRM HDCP protocol definitions for `mei_hdcp.c`.

Important APIs and types: it includes `<drm/display/drm_hdcp.h>`, which supplies HDCP 2.2 message structures, constants, and helper declarations used by the MEI HDCP command translator.

Control flow: none; this is a compile-time dependency header.

State and persistence: no state.

Dependencies and integration: couples the MEI HDCP client to DRM display HDCP structures instead of duplicating protocol layouts locally. This keeps message fields aligned with display core expectations.

Risks: because the header currently contains no local declarations, changes to DRM HDCP headers can directly break `mei_hdcp.c`. Adding local command declarations here in the future would need careful separation from UAPI/DRM protocol structs.

Test signals: compile coverage of `mei_hdcp.c`, especially after DRM HDCP header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me-regs.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me-regs.h

Purpose: defines PCI device IDs, PCI firmware-status offsets, MEI memory-mapped register offsets, and bit masks for the classic Intel ME/HECI hardware backend.

Important APIs and constants: device IDs cover legacy ICH/ICH10, PCH generations, server chipsets, Atom/embedded variants, GSC/GSCFI/CSC-style devices, and newer named platforms. Firmware-status offsets include `PCI_CFG_HFS_1` through `PCI_CFG_HFS_6` and SKU/PM/PXP masks. Register offsets include `H_CB_WW`, `H_CSR`, `ME_CB_RW`, `ME_CSR_HA`, `H_HPG_CSR`, `H_D0I3C`, and GSC extended operation memory registers. Bit masks describe host and ME circular-buffer depth/pointers, ready/reset/interrupt bits, PG isolation, D0i3, and TRC status.

Control flow: no executable code. `hw-me.c` uses these constants to read/write hardware, compute buffer slots, control interrupts, perform resets, negotiate power gating, read FW status, and configure platform quirks.

State and persistence: no in-memory state. Values map persistent hardware registers exposed by PCI config space or MMIO.

Dependencies and integration: included by `hw-me.c` and likely PCI ID tables outside this subset. The SPDX dual license allows reuse in GPL/BSD-compatible contexts for register definitions.

Risks: incorrect offsets or masks can corrupt hardware communication, mis-detect firmware SKU, break D0i3/PG handling, or falsely enable unsupported platforms. Device ID additions must match platform configuration selection in the ME PCI driver and `mei_cfg_idx`.

Test signals: probe success on each platform ID, correct sysfs `fw_status` output, interrupt delivery through `H_CSR`/`ME_CSR_HA`, runtime PM D0i3 transitions, TRC tracepoint register reads, and PXP/GSC boot-type detection on GSC devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.c

Purpose: implements the `mei_hw_ops` backend for classic Intel ME/GSC-style MEI hardware using host and ME circular buffers, PCI firmware-status registers, H_CSR/ME_CSR handshakes, interrupts or polling, and runtime power management.

Important APIs and functions: exported functions are `mei_me_irq_quick_handler()`, `mei_me_irq_thread_handler()`, `mei_me_polling_thread()`, `mei_me_get_cfg()`, `mei_me_dev_init()`, `mei_me_pg_enter_sync()`, and `mei_me_pg_exit_sync()`. Local functions implement MMIO access, FW/TRC status reads, hardware config, interrupt enable/disable/clear, reset/start, host-buffer slot accounting, write/read slots, legacy PGI, D0i3 entry/exit, GSC PXP detection, quirk probes for NM/SPS/IGN firmware, platform `mei_cfg` instances, and the `mei_me_hw_ops` table.

Control flow: initialization allocates a `mei_device` plus `mei_me_hw`, installs common core state via `mei_device_init()`, copies DMA sizes from the selected platform config, and records kind/FW-version support. `mei_start()` calls `hw_config`, `hw_reset`, and `hw_start` through ops. Reset manipulates `H_RST`, `H_IG`, `H_RDY`, interrupt bits, and D0i3 state; start waits for firmware ready, checks GSC PXP mode, releases reset, and marks host ready. The quick IRQ handler disables device interrupts and wakes the thread. The thread clears interrupt status, reacts to firmware reset/not-ready, handles PG/D0i3 interrupts, wakes start waiters, processes inbound slots through `mei_irq_read_handler()`, writes pending queued messages through `mei_irq_write_handler()`, completes callbacks, and re-enables interrupts.

State and persistence: hardware state is in registers; driver state is volatile in `struct mei_me_hw`: config pointer, MMIO base, IRQ, PG/D0i3 state, buffer depth, FW-status reader, polling thread, and activity waitqueue. `struct mei_device` carries reset counters, PG events, PXP mode, HBM state, queues, and DMA descriptors.

Dependencies and integration: depends on `hw-me-regs.h`, `mei_dev.h`, `hbm.h`, tracepoints, PCI config access, kthreads, runtime PM, wait queues, and IRQ infrastructure. It is selected by PCI/platform probe code outside this subset and consumed through the generic MEI core ops wrappers in `mei_dev.h`.

Risks: register bit semantics are delicate. Write-one-to-clear interrupt bits require masking through `mei_hcsr_set()`. H_RST already set before reset needs clearing or reset can be ignored. D0i3 and legacy PGI use multiple wait states and can deadlock or time out if interrupts are lost. The interrupt thread schedules reset on unexpected firmware-not-ready or bad read results, so false positives can cause reset loops. Platform quirk probes read function 0 PCI config and must align with SKU definitions.

Test signals: boot/probe on multiple generations, interrupt and polling modes, reset storm limit behavior, sysfs `fw_status`/`trc`, runtime PM suspend/resume, GSC PXP boot path, DMA-ring negotiation on configured platforms, ftrace `mei_reg_read/write` and `mei_pci_cfg_read`, and fault injection for HBM read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.h

Purpose: declares ME hardware configuration structures, the ME hardware private state, platform configuration indexes, and public entry points for the classic ME/GSC hardware backend.

Important APIs and types: `struct mei_cfg` describes generation-specific FW status registers, optional firmware-exclusion quirk, kind string, DMA descriptor sizes, FW-version support, and TRC support. `struct mei_me_hw` stores config, MMIO address, IRQ, PG state, D0i3 support, host-buffer depth, FW status reader callback, and optional polling-thread state. `enum mei_cfg_idx` indexes the platform config table and must match `mei_cfg_list[]` in `hw-me.c`. Public functions include `mei_me_get_cfg()`, `mei_me_dev_init()`, PG enter/exit, IRQ handlers, and polling thread.

Control flow: PCI probe code selects a `mei_cfg` index, obtains it with `mei_me_get_cfg()`, calls `mei_me_dev_init()`, wires MMIO/IRQ fields, and registers/start the common MEI device. Interrupt and PM code use the declared handlers.

State and persistence: no storage in the header. It defines the layout embedded after `struct mei_device` allocation and accessed with `to_me_hw(dev)`.

Dependencies and integration: includes PCI, IRQ, MEI public headers, `mei_dev.h`, and `client.h`. The enum and config table are a strict cross-file ABI inside the driver.

Risks: enum/table desynchronization selects wrong platform behavior. The `to_me_hw` cast assumes `struct mei_me_hw` is allocated immediately after `struct mei_device`; allocation changes must preserve that layout. Polling mode is inferred from negative IRQ and must be initialized consistently by probe.

Test signals: build coverage for all config enum users, probe using every config index present in PCI ID tables, D0i3/runtime PM tests, and polling-mode tests when no IRQ is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe-regs.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe-regs.h

Purpose: defines register offsets, bit masks, BAR indexes, firmware status offsets, timeouts, payload size, and SATT range constants for Intel TXE/SeC MEI hardware.

Important APIs and constants: BAR indexes are `SEC_BAR` and `BRIDGE_BAR`. Firmware status offsets are `PCI_CFG_TXE_FW_STS0` and `PCI_CFG_TXE_FW_STS1`. IPC registers cover input doorbell/status/payload, host interrupt status/mask, shared/output payload, high-level interrupt hierarchy, readiness, aliveness, output status, and bridge/SATT translation registers. Bit masks identify readiness, aliveness, output-doorbell, input-ready, illegal memory, crypto-key errors, and timer overflow interrupt bits. `PAYLOAD_SIZE` is 64 bytes, matching TXE fixed IPC payload size.

Control flow: no executable logic. `hw-txe.c` uses these constants to synchronize aliveness/readiness, write payloads, read output payloads, translate interrupt causes, acknowledge interrupt hierarchy, and expose firmware status.

State and persistence: no driver state here; constants map hardware state.

Dependencies and integration: includes `hw.h` for shared MEI slot sizing and bit helpers. The register map supports the TXE `mei_hw_ops` implementation.

Risks: TXE uses two BARs and hierarchical interrupts; wrong offset or acknowledgment ordering can lose interrupts or wedge IPC. `PAYLOAD_SIZE` drives buffer-depth calculations, so changing it without hardware support would corrupt message framing.

Test signals: TXE hardware probe/start, aliveness/readiness timeouts, input-ready interrupt, output-doorbell read path, firmware status sysfs output, and stress tests of repeated reset/start cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.c

Purpose: implements the `mei_hw_ops` backend for Intel TXE/SeC hardware, which differs from classic ME by using fixed-size IPC payload RAM, input/output doorbells, readiness/aliveness registers, and hierarchical interrupt registers across SEC and bridge BARs.

Important APIs and functions: exported functions are `mei_txe_dev_init()`, `mei_txe_irq_quick_handler()`, `mei_txe_irq_thread_handler()`, and `mei_txe_aliveness_set_sync()`. Local helpers implement SEC/bridge register access, aliveness request/response polling or waiting, readiness setup/clear/wait, interrupt clear/enable/disable/translation, payload read/write, reset/start, FW status reads, PG state reporting, and the `mei_txe_hw_ops` table.

Control flow: reset disables interrupts, reconciles aliveness request/response, clears aliveness if asserted, and clears host readiness. Start enables interrupts, waits for SeC readiness, clears stale output-doorbell status, asserts aliveness, enables input-ready interrupts, marks output ready, and sets host ready. Writes require aliveness and input-ready status, place header/data dwords into SEC input payload RAM, mark `hw->slots = 0`, and ring input doorbell. Reads consume the bridge output payload after the header and then mark output ready. The quick handler translates/acks pending high-level, bridge, and SEC interrupts into `hw->intr_cause`; the threaded handler processes readiness, aliveness, output-doorbell reads, input-ready writes, and callback completion.

State and persistence: `struct mei_txe_hw` stores BAR pointers, cached aliveness/readiness, available slots, waitqueue for aliveness responses, and `intr_cause` bits. State is volatile and rebuilt on reset/probe.

Dependencies and integration: depends on PCI config access, ktime/jiffies delays, runtime PM, common MEI client/HBM/interrupt helpers, and `hw-txe-regs.h`. Like `hw-me.c`, it plugs into common MEI core solely through `mei_hw_ops`.

Risks: TXE write path warns if `data` is NULL even when only a header is written, which differs from classic ME semantics and relies on callers providing a payload pointer. Aliveness transitions use both interrupt wait and polling depending on reset stage; missed transitions produce `-ETIME`/`-EIO`. The interrupt hierarchy must be acknowledged in correct order. The read-slot count always returns the fixed payload depth, so header length validation in common interrupt code is the main protection against malformed firmware output.

Test signals: reset/start on TXE platforms, aliveness wait/poll timeout tests, input-ready write queue drain, output-doorbell HBM/client message reception, MSI and non-MSI interrupt handling, repeated suspend/resume, and fault injection for readiness loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.h

Purpose: declares TXE backend constants, private hardware state, helpers, and public entry points.

Important APIs and types: interrupt-cause bits map readiness, aliveness, output-doorbell, and input-ready events into a flattened mask. `struct mei_txe_hw` stores SEC/bridge BAR pointers, cached aliveness/readiness, write slots, aliveness waitqueue, and translated interrupt causes. Public functions include `mei_txe_dev_init()`, quick/thread IRQ handlers, and `mei_txe_aliveness_set_sync()`.

Control flow: PCI TXE probe code allocates a `mei_device` with TXE private state via `mei_txe_dev_init()`, maps BARs into `mem_addr`, requests IRQs using the declared handlers, and starts the common MEI core. Runtime PM can call aliveness synchronization to keep or release the SeC.

State and persistence: defines volatile per-device TXE state accessed with `to_txe_hw(dev)`. No persistent storage.

Dependencies and integration: includes IRQ return types, shared `hw.h`, and TXE register definitions. The allocation layout uses `hw_txe_to_mei()` and `to_txe_hw()` casts.

Risks: the `mem_addr` field is a pointer to a const array of BAR mappings; probe must keep that array alive for device lifetime. Cast-based embedding assumes allocation layout exactly matches `mei_txe_dev_init()`.

Test signals: compile/probe on TXE PCI devices, interrupt flattening behavior, runtime PM aliveness transitions, and KASAN coverage for BAR pointer lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw.h

Purpose: centralizes shared MEI wire protocol constants, HBM command IDs, version feature gates, extended-header formats, bus message headers, and host/firmware message structures used by all MEI backends and HBM code.

Important APIs and types: defines global timeouts, `HBM_MAJOR_VERSION`/`HBM_MINOR_VERSION`, feature-version constants for PGI, dynamic clients, immediate enum, disconnect-on-timeout, events, fixed-address clients, OS version, DMA rings, vtags, GSC, capabilities, and client DMA. It declares HBM command IDs, `enum mei_hbm_status`, connection/disconnection status enums, extended header types and structs (`mei_ext_hdr`, `mei_ext_meta_hdr`, vtag and GSC headers), `struct mei_msg_hdr`, and many packed HBM request/response structures such as host start/stop, enum, properties, client connect/disconnect, flow control, PG, notify, DMA setup, capability, and client DMA commands.

Control flow: not executable except inline helpers for extended-header traversal/length. Runtime code uses these layouts to serialize/deserialize all HBM and data messages. `mei_msg_hdr` drives common read/write slot framing, routing by host/ME addresses, completion bits, DMA ring flag, and extended-header flag.

State and persistence: no storage. It defines protocol bytes that are exchanged with firmware and therefore must stay stable.

Dependencies and integration: included by HBM, hardware backends, TXE regs, and common device/client code. It also includes public `<linux/mei.h>` for externally visible MEI structures.

Risks: packed wire layout changes are high risk because firmware consumes exact binary formats. Extended-header length is expressed in dwords and traversal assumes valid firmware lengths after interrupt-side validation. Version feature constants gate optional behavior; incorrect thresholds can enable unsupported protocol commands.

Test signals: build-time `BUILD_BUG_ON` size checks in HBM code, runtime HBM negotiation, vtag/GSC extended-header message tests, DMA-ring/client-DMA tests, and fuzz/fault injection of malformed message headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/init.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/init.c

Purpose: implements common MEI device lifecycle management: state string helpers, firmware-status formatting, work cancellation, reset/start/restart/stop flows, write-idle detection, and base `mei_device` initialization.

Important APIs and functions: exported functions are `mei_dev_state_str()`, `mei_pg_state_str()`, `mei_fw_status2str()`, `mei_cancel_work()`, `mei_reset()`, `mei_start()`, `mei_restart()`, `mei_stop()`, `mei_write_is_idle()`, and `mei_device_init()`. Internal `mei_reset_work()` retries resets asynchronously after IRQ-detected errors.

Control flow: `mei_start()` locks the device, clears interrupts, runs hardware config, repeatedly performs reset until success or disable, waits for HBM start, validates HBM version, and leaves the link established. `mei_reset()` logs unexpected reset context, clears interrupts, idles HBM, marks resetting, enforces a consecutive reset limit, calls hardware reset/start through ops, disconnects software clients except power-up/initialization cases, clears HBM/client/FW-version/read-header state, enters `MEI_DEV_INIT_CLIENTS`, and sends the HBM start request. `mei_restart()` is suspend/resume-oriented and schedules retry on partial failure. `mei_stop()` transitions through powering-down states, removes MEI bus devices, cancels work, synchronizes IRQs, resets to disabled, and disconnects clients.

State and persistence: initializes and mutates volatile `struct mei_device` state: device state, waitqueues, locks, work items, host/client lists, callback queues, tx queue limit, host client bitmap, reset count, PXP/GSC reset flags, PG event, ops pointer, parent device, and timeout values. No persistent storage beyond hardware state.

Dependencies and integration: calls generic hardware ops wrappers, HBM start/reset helpers, client disconnect and bus removal/rescan helpers, workqueues, waitqueues, and runtime-safe IRQ synchronization. Hardware backends call `mei_device_init()` during allocation.

Risks: reset flow is central and can race with IRQ handlers, runtime PM, and userspace file operations; most callers must hold `device_lock`. Reset loops are capped by `MEI_MAX_CONSEC_RESET`, after which the device is disabled. `mei_stop()` intentionally cancels work twice to catch HW-initiated reset during shutdown.

Test signals: probe/start success, forced reset recovery, suspend/resume via `mei_restart()`, shutdown/remove via `mei_stop()`, sysfs `dev_state` transitions, reset-count disable after repeated failures, and idle detection before runtime PM autosuspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/interrupt.c

Purpose: provides common interrupt-thread logic for reading firmware messages, dispatching HBM/control/data packets, draining write queues, completing callbacks, and detecting protocol stalls/timeouts. Hardware backends call these routines after platform-specific IRQ acknowledgment.

Important APIs and functions: exported functions are `mei_irq_compl_handler()`, `mei_irq_read_handler()`, `mei_irq_write_handler()`, `mei_schedule_stall_timer()`, and `mei_timer()`. Local helpers validate message headers, discard unread payloads, route client messages, process extended vtag/GSC headers, send disconnect responses and flow-control requests, and handle connect/disconnect timeouts.

Control flow: `mei_irq_read_handler()` reads a MEI header if not already cached, validates reserved bits and minimum extended/DMA lengths, reads extended metadata and DMA length slots, dispatches HBM packets to `mei_hbm_dispatch()`, routes client packets by host/ME address, discards fixed-address or power-down orphan messages, and resets cached header state before recounting slots. `mei_cl_irq_read_msg()` attaches received fragments to pending read callbacks, validates vtag/GSC extended headers, reads from DMA ring or hardware slots, completes callbacks when `msg_complete` is set, and requests autosuspend on partial messages. `mei_irq_write_handler()` acquires the host buffer, completes write-waiting callbacks, then drains control writes and normal writes in order. `mei_timer()` handles HBM init stalls and per-client connect/disconnect timeouts.

State and persistence: mutates volatile callback lists (`write_waiting_list`, `ctrl_wr_list`, `write_list`, `rd_pending`, completion list), cached read headers, per-client read buffers, vtags, GSC ext headers, status fields, timer counters, and waitqueues. No persistent storage.

Dependencies and integration: depends on `hbm.h`, `client.h`, DMA ring helpers, runtime PM, kthreads/workqueues, common hardware read/write wrappers, and hardware backend IRQ threads.

Risks: malformed firmware headers can trigger resets; some paths return `-EBADMSG`, `-ENODATA`, `-ERANGE`, or `-EPROTO` to backend IRQ threads. Extended-header parsing depends on validated dword sizes and can allocate per-callback GSC header memory. Missing read callbacks are tolerated only for fixed-address clients. The write path assumes callbacks are correctly queued by client code and can return `-EMSGSIZE` when hardware buffer space is insufficient.

Test signals: interrupt-driven read/write under userspace traffic, fragmented multi-packet reads, vtag mismatch rejection, GSC extended-header handling, DMA-ring reads, fixed-address orphan discard, flow-control issuance, connect timeout behavior with and without disconnect-on-timeout support, and reset on corrupted headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/main.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/main.c

Purpose: implements the MEI character-device interface, sysfs attributes, minor allocation/registration, module initialization, and userspace-facing file operations for connecting to firmware clients and exchanging messages.

Important APIs and functions: file operations are `mei_open()`, `mei_release()`, `mei_read()`, `mei_write()`, `mei_ioctl()`, `mei_poll()`, `mei_fsync()`, and `mei_fasync()`. IOCTL helpers handle plain and vtagged connect, notification set/get, and vtag support checks. Sysfs attributes expose `fw_status`, `hbm_ver`, `hbm_ver_drv`, `tx_queue_limit`, `fw_ver`, `dev_state`, `trc`, and `kind`. Exported registration functions are `mei_register()`, `mei_deregister()`, and `mei_set_devstate()`.

Control flow: module init registers class, char-dev major range, and MEI client bus. Hardware probe calls `mei_register()` to allocate a minor, initialize/cdev/device, add sysfs groups, and register debugfs. `open` validates enabled state, allocates a linked `mei_cl`, and stores it in `file->private_data`. `ioctl` connects to a firmware UUID, optionally with vtags that share an existing connected client across file descriptors. `write` validates connection, MTU, activity, and tx queue limit before allocating a callback and queuing it. `read` starts a read callback if needed, waits unless nonblocking, copies completed callback data to userspace, and handles partial user reads through file offset. `poll` starts reads opportunistically and reports read/write/notification readiness.

State and persistence: global runtime state includes `mei_devt`, class, IDR of devices, minor lock, and per-device sysfs/cdev objects. Per-open state is `struct mei_cl` plus vtag mappings associated with file pointers. `tx_queue_limit` is mutable through sysfs but not persisted across reload/reboot.

Dependencies and integration: uses Linux char device APIs, IDR, sysfs, poll/fasync, runtime PM for FW status reads, MEI client/bus APIs, HBM version constants, and client queue helpers. Hardware backends register common MEI devices through this file.

Risks: file operations rely on `device_lock` for client and queue state. `release` may drop the lock during disconnect and must re-check vtag mappings afterward. Read/write paths must avoid sleeping while locked except through explicit unlock/wait/relock sections. Vtag sharing rejects duplicate or mismatched tags but has complex replacement logic. IOCTL copies can fail after connection state has changed, leaving a connected kernel client despite `-EFAULT`.

Test signals: `/dev/mei*` open/connect/read/write with blocking and nonblocking I/O, ioctl ABI tests for vtag and notification commands, poll/epoll readiness, sysfs attribute reads/writes, concurrent open/release with vtags, device deregistration while files are open, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.c

Purpose: instantiates and exports MEI tracepoints for register and PCI config access.

Important APIs and functions: defines `CREATE_TRACE_POINTS`, includes `mei-trace.h`, and exports `mei_reg_read`, `mei_reg_write`, and `mei_pci_cfg_read` tracepoint symbols when not under sparse `__CHECKER__`.

Control flow: compile-time tracepoint generation only. Runtime users enable the tracepoints through ftrace/perf/tracefs; hardware code calls `trace_mei_*` helpers generated from `mei-trace.h`.

State and persistence: tracepoint enablement and ring-buffer data are managed by kernel tracing infrastructure. This file owns no driver state.

Dependencies and integration: depends on Linux module and tracepoint infrastructure and the local trace header. `hw-me.c`, `hw-txe.c`, and quirk/FW-status paths use the emitted tracepoints for observability.

Risks: tracepoint symbol names are ABI-like for in-kernel users; renaming them breaks out-of-tree instrumentation. The sparse guard avoids macro issues during static analysis but also means sparse does not instantiate tracepoint bodies here.

Test signals: build with tracing enabled, `tracefs` listing of `mei:mei_reg_read`, `mei:mei_reg_write`, and `mei:mei_pci_cfg_read`, and captured events during MEI probe/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.h

Purpose: declares MEI trace events for MMIO register reads, MMIO register writes, and PCI configuration reads.

Important APIs and types: `TRACE_SYSTEM mei` groups the events. `TRACE_EVENT(mei_reg_read)` records device name, register label, offset, and value. `TRACE_EVENT(mei_reg_write)` records analogous write data. `TRACE_EVENT(mei_pci_cfg_read)` records device name, register label, PCI config offset, value, and return code. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct trace generation to this local header.

Control flow: trace macros expand into static tracepoint call sites and metadata. Hardware code calls generated `trace_mei_reg_read()`, `trace_mei_reg_write()`, and `trace_mei_pci_cfg_read()` helpers; enabled tracepoints emit formatted events.

State and persistence: no driver state. Trace buffers are external kernel tracing state.

Dependencies and integration: includes Linux stringify/types/tracepoint/device headers. The header must be included once with `CREATE_TRACE_POINTS` from `mei-trace.c` and may be included by hardware code for call-site declarations.

Risks: format-string or field changes affect tooling that parses trace output. The final `#include <trace/define_trace.h>` must remain outside the include guard per tracing conventions.

Test signals: kernel build tracepoint generation, event presence under `/sys/kernel/tracing/events/mei/`, and register/PCI events while probing or resetting MEI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.h -->
