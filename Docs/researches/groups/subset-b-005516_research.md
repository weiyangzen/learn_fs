# subset-b-005516 Research

Grouped source research for xHCI sideband access, NVIDIA Tegra XUSB host integration, and xHCI tracepoint instantiation/definitions. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-sideband.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-sideband.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci-sideband.c` implements the exported xHCI sideband API used by external client drivers to share selected xHCI endpoint transfer rings and secondary interrupter event rings with a non-host execution agent. The source was read as a complete 494-line file. Its practical role is to let a sideband client register ownership against a USB interface, add non-stream endpoints, obtain scatter-gather descriptions for controller-owned rings, create/remove a secondary interrupter, and tear the whole association down without leaving xHCI virtual-device state marked as offloaded.

## Important APIs, Types, and Functions

Important exported entry points are `xhci_sideband_register`, `xhci_sideband_unregister`, `xhci_sideband_add_endpoint`, `xhci_sideband_remove_endpoint`, `xhci_sideband_stop_endpoint`, `xhci_sideband_get_endpoint_buffer`, `xhci_sideband_get_event_buffer`, `xhci_sideband_create_interrupter`, `xhci_sideband_remove_interrupter`, `xhci_sideband_interrupter_id`, `xhci_sideband_check`, and `xhci_sideband_notify_ep_ring_free`. Internal helpers are `xhci_ring_to_sgtable`, `__xhci_sideband_remove_endpoint`, and `__xhci_sideband_remove_interrupter`.

The central data object is `struct xhci_sideband` from the public sideband header. This file populates its `xhci`, `vdev`, `intf`, `type`, `notify_client`, `ir`, `eps[]`, and `mutex` fields and also writes the reciprocal `struct xhci_virt_device::sideband` and `struct xhci_virt_ep::sideband` links. It depends on xHCI-internal objects such as `struct xhci_hcd`, `struct xhci_virt_device`, `struct xhci_virt_ep`, `struct xhci_ring`, `struct xhci_segment`, and secondary interrupter allocation/removal helpers.

## Control Flow

Registration starts from a USB interface. `xhci_sideband_register` derives the USB device, HCD, and `struct xhci_hcd`, rejects unaddressed devices and all types except `XHCI_SIDEBAND_VENDOR`, allocates a sideband object, initializes its mutex, and then takes `xhci->lock` to verify and install exclusive sideband ownership on `xhci->devs[slot_id]`. Endpoint handoff is separate: `xhci_sideband_add_endpoint` locks the sideband mutex, verifies the virtual device still exists, converts the host endpoint descriptor to an xHCI endpoint index, rejects stream-capable endpoints and endpoints already used by any sideband, then stores both the endpoint-side and sideband-side links.

Ring access flows through `xhci_sideband_get_endpoint_buffer` or `xhci_sideband_get_event_buffer`, both of which validate the sideband relationship and call `xhci_ring_to_sgtable`. That helper walks the ring segments, translates each segment DMA allocation into pages with `dma_get_sgtable`, builds a combined scatterlist with `sg_alloc_table_from_pages`, and stores the first segment DMA address in `sg_dma_address(sgt->sgl)` so the client can discover the ring IOVA. Interrupter flow is similarly explicit: `xhci_sideband_create_interrupter` creates one secondary interrupter for the sideband, configures `ip_autoclear`, and exposes its target ID through `xhci_sideband_interrupter_id`; removal calls `xhci_remove_secondary_interrupter`.

Unregistration is the cleanup root. `xhci_sideband_unregister` takes the sideband mutex, removes every tracked endpoint by issuing synchronous stop-endpoint commands, removes the secondary interrupter, clears `sb->vdev`, then takes `xhci->lock` to clear `sb->xhci` and `vdev->sideband` before freeing the sideband object.

## State and Persistence Behavior

The file owns only in-kernel lifetime state. There is no file-backed persistence. Sideband state persists while a registered client holds the `struct xhci_sideband` pointer. Endpoint state is represented by reciprocal pointers in `sb->eps[]` and `ep->sideband`; virtual-device state is represented by `vdev->sideband`; event routing state is represented by `sb->ir`. Ring memory is not allocated here and remains owned by xHCI, while callers receive temporary `struct sg_table` objects that they must free.

Concurrency is split between `sb->mutex` for sideband membership/interrupter changes and `xhci->lock` for virtual-device ownership. Endpoint removal synchronously stops the endpoint so xHCI command completion can perform ring cleanup before client access is considered invalid. `xhci_sideband_notify_ep_ring_free` sends a synchronous callback opportunity to the sideband client before a transfer ring is freed.

## Dependencies and Integration Points

Direct dependencies are `<linux/usb/xhci-sideband.h>`, `<linux/dma-direct.h>`, and `"xhci.h"`. The API integrates with USB interface drivers that need vendor sideband/offload behavior, xHCI virtual device and endpoint internals, the secondary interrupter allocator, DMA scatterlist helpers, and USB offload power-management checks via `usb_offload_check`. The sideband client must know how to write xHCI TRBs and target the returned interrupter ID when routing completion events.

## Risks and Edge Cases

The largest correctness risk is ownership lifetime: a sideband client must stop touching endpoint and event rings after removal or unregister, because the backing xHCI ring storage may be cleaned up immediately after the synchronous callbacks. `xhci_ring_to_sgtable` exposes controller DMA memory to another agent; DMA mask mismatches are called out in a comment and can make a sideband device unable to access the returned IOVA. Stream endpoints are rejected, so clients requiring bulk streams need a different model. Error handling in the sg-table conversion is sensitive to partial allocation and page accounting; callers must treat a `NULL` return as no safe ring access. Power-management users of `xhci_sideband_check` must first ensure downstream devices are marked offload-PM-locked, otherwise the active-sideband answer can be stale.

## Test Signals

Useful signals include module build coverage with `CONFIG_USB_XHCI_SIDEBAND`, sideband registration/unregistration under device disconnect, endpoint add/remove on all endpoint types with streams rejected, secondary interrupter create/remove and target-ID routing, sg-table validation against multi-segment endpoint and event rings, ring-free callback ordering, and runtime/system suspend paths using `xhci_sideband_check` while offload devices are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-sideband.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-tegra.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci-tegra.c` is the NVIDIA Tegra XUSB platform driver that adapts the generic xHCI host controller to Tegra SoC clocks, resets, power domains, firmware, pad controller, PHYs, mailbox protocol, wake events, OTG role handling, and ELPG low-power transitions. The source was read as a complete 2,853-line file. It creates the primary USB2 and shared USB3 HCDs, boots or attaches to the XUSB Falcon firmware, exposes SoC-specific resource tables for Tegra124/210/186/194/234, and overrides selected xHCI operations to keep UTMI pads powered correctly around USB2 hub control.

## Important APIs, Types, and Functions

Core data structures are `struct tegra_xusb_fw_header`, `struct tegra_xusb_phy_type`, `struct tegra_xusb_mbox_regs`, `struct tegra_xusb_context_soc`, `struct tegra_xusb_soc_ops`, `struct tegra_xusb_soc`, `struct tegra_xusb_context`, `struct tegra_xusb`, and `struct tegra_xusb_mbox_msg`. The SoC tables define firmware names, supply names, PHY counts, port bit offsets, context-save registers, mailbox offsets, CSB access operations, low-power support, BAR2/IPFS presence, and wake IRQ capacity.

Important probe/lifecycle functions are `tegra_xusb_probe`, `tegra_xusb_remove`, `tegra_xusb_shutdown`, `tegra_xusb_disable`, `tegra_xusb_init`, and `tegra_xusb_exit`. Hardware access helpers include `fpci_readl`, `ipfs_readl`, `bar2_readl`, `fpci_csb_readl`, `bar2_csb_readl`, and their write variants. Firmware and mailbox functions include `tegra_xusb_request_firmware`, `tegra_xusb_load_firmware_rom`, `tegra_xusb_init_ifr_firmware`, `tegra_xusb_load_firmware`, `tegra_xusb_wait_for_falcon`, `tegra_xusb_mbox_send`, `tegra_xusb_mbox_irq`, `tegra_xusb_mbox_thread`, and `tegra_xusb_mbox_handle`.

Power and PHY functions include `tegra_xusb_clk_enable`, `tegra_xusb_clk_disable`, `tegra_xusb_phy_enable`, `tegra_xusb_phy_disable`, `tegra_xusb_unpowergate_partitions`, `tegra_xusb_powergate_partitions`, `tegra_xusb_enter_elpg`, `tegra_xusb_exit_elpg`, `tegra_xusb_suspend`, `tegra_xusb_resume`, `tegra_xusb_runtime_suspend`, and `tegra_xusb_runtime_resume`. OTG and hub integration are handled by `tegra_xusb_init_usb_phy`, `tegra_xhci_id_notify`, `tegra_xhci_id_work`, `tegra_xhci_set_port_power`, `tegra_xhci_hub_control`, `tegra_xhci_setup`, and `tegra_xhci_quirks`.

## Control Flow

Probe allocates `struct tegra_xusb`, initializes context buffers, maps host/FPCI/IPFS or BAR2 resources, obtains the xHCI and mailbox IRQs, sets up optional wake IRQs, gets padctl, clocks, resets or generic power domains, regulators, and all named PHYs. It creates the main HCD, enables clocks/regulators/PHYs, sets a 40-bit DMA mask for Falcon-visible memory, requests firmware when required, unpowergates partitions, configures FPCI BARs and bus-mastering, loads firmware, adds the main USB2 HCD, creates/adds the shared USB3 HCD, requests mailbox and padctl interrupts, enables firmware messages, initializes optional USB PHY/OTG notifications, and finally enables runtime PM when padctl IRQ support exists.

Mailbox control starts in `tegra_xusb_mbox_irq`, which clears SMI interrupt status and wakes the threaded handler. `tegra_xusb_mbox_thread` serializes with `tegra->lock`, ignores mailbox work while runtime-suspended or system-suspended, unpacks the firmware message from `data_out`, clears `MBOX_DEST_SMI`, releases ownership for no-ACK commands, and dispatches to `tegra_xusb_mbox_handle`. The handler acknowledges or rejects firmware requests for Falcon/SS clock changes, bandwidth notification, USB3 DFE/CTLE context save, HSIC idle transitions, LFPS detection toggles, and other recognized operations. Responses go back through `tegra_xusb_mbox_send`, which arbitrates mailbox ownership unless sending ACK/NAK.

Firmware loading has two paths. Older SoCs request a firmware blob, allocate coherent DMA memory, copy the image, program Falcon IMEM/DFI registers through CSB, trigger L2IMEM loading, set the boot vector, start Falcon, and wait for xHCI controller-not-ready to clear. Tegra234-style IFR firmware skips blob loading and reads firmware header data through BAR2 firmware-scratch IOCTLs after waiting for Falcon readiness.

Low-power entry and exit are the most complex control paths. `tegra_xusb_enter_elpg` disables event interrupts, verifies enabled ports are suspended, records UTMI LP0 pad state, calls `xhci_suspend`, saves FPCI/IPFS context registers, enables PHY sleepwalk/wake if wakeup is allowed, powergates partitions, powers off PHYs, and disables clocks. `tegra_xusb_exit_elpg` reverses that order: clocks, partitions, wake disable, PHY init/power-on, optional UTMI LP0 pad programming, FPCI/IPFS reconfiguration and context restore, firmware reload/message enable, sleepwalk disable, `xhci_resume`, and event-interrupt re-enable. System suspend/resume wrap ELPG with wake IRQ enable/disable and runtime-PM state correction; runtime suspend/resume run the same ELPG transitions with `is_auto_resume` set.

## State and Persistence Behavior

The driver stores all runtime state in `struct tegra_xusb`, including MMIO bases, IRQs, wake IRQ list, clocks, resets, generic power-domain devices, regulators, PHY arrays, USB PHY/OTG state, firmware DMA allocation, suspend flag, context-save buffers, LP0 UTMI pad mask, and SoC description. Persistent hardware state includes the controller firmware image in coherent memory while the driver is bound, Falcon-loaded firmware during active power, FPCI/IPFS context registers saved across ELPG, xHCI internal device/ring state managed by the core HCD, and padctl sleepwalk/wake configuration during low-power states.

`tegra->lock` serializes mailbox handling and suspend/resume transitions. Runtime PM uses autosuspend and marks the device last-busy before ELPG exit and after failed ELPG entry. The remove path deinitializes USB PHY OTG hooks, resumes runtime PM, removes shared and main HCDs, frees firmware coherent memory, disables runtime PM if enabled, powers down partitions/PHYs/clocks/regulators, and releases padctl. There is no filesystem persistence beyond requested firmware files named by the SoC table.

## Dependencies and Integration Points

This file sits at the intersection of the platform bus, xHCI core, USB core, Tegra padctl, generic PHY, legacy USB PHY/OTG, regulators, clocks, reset controls, firmware loader, DMA API, runtime/system PM, generic PM domains, IRQ wake, and Tegra PMC powergate APIs. Direct xHCI integration is via `usb_create_hcd`, `usb_create_shared_hcd`, `usb_add_hcd`, `xhci_gen_setup`, `xhci_suspend`, `xhci_resume`, `xhci_shutdown`, and the `xhci_driver_overrides` hook for setup and hub control. Device-tree integration is through compatible strings for `nvidia,tegra124-xusb`, `tegra210`, `tegra186`, `tegra194`, and `tegra234`, named resources, clocks, PHYs, supplies, power domains, and padctl phandle/interrupts.

## Risks and Edge Cases

Ordering is the main risk. Probe and ELPG paths depend on exact sequencing of clocks, regulators, PHY power, partition power, FPCI/BAR setup, firmware load, HCD registration, and IRQ enablement. Any early-return path must unwind in the reverse order, and runtime PM can otherwise leave partitions or PHYs active. Firmware mailbox ownership can time out or race with suspend; the threaded handler intentionally ignores messages while suspended, so firmware commands during transitions need validation. `tegra_xusb_check_ports` rejects ELPG if enabled ports have not reached U3; flaky devices can block autosuspend. Wake behavior depends on padctl IRQ presence, optional wake IRQs, sleepwalk support, and accurate port-speed decoding. OTG handling depends on optional legacy USB PHY notifiers and companion USB3 lookup, so role changes can affect port power and SSPI reset behavior. SoC tables are ABI-like: wrong port offsets, mailbox offsets, context offsets, or PHY counts can silently break hardware-specific behavior.

## Test Signals

High-value signals are boot/probe on every compatible SoC table, firmware load and timestamp logging, USB2/USB3 enumeration, shared-HCD stream capability, mailbox ACK/NAK handling for SS clock, HSIC idle, LFPS, and DFE/CTLE commands, runtime autosuspend/resume with all ports suspended, failed autosuspend with an active port, system suspend/resume with wake-capable devices, remote wake through padctl sleepwalk, OTG ID role switches with USB2 and USB3 companion ports, remove/shutdown after active transfers, and trace/dmesg checks for controller-not-ready, mailbox busy, failed powergate, and failed PHY operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.c` is the single translation unit that instantiates the xHCI tracepoints declared in `xhci-trace.h`. The source was read as a complete 15-line file. It exists so the tracepoint header can be included widely without creating duplicate tracepoint definitions, while this file defines `CREATE_TRACE_POINTS` once and exports selected tracepoint symbols for other GPL modules.

## Important APIs, Types, and Functions

The file defines `CREATE_TRACE_POINTS`, includes `"xhci-trace.h"`, and exports `xhci_dbg_quirks` and `xhci_dbg_init` with `EXPORT_TRACEPOINT_SYMBOL_GPL`. It has no callable functions of its own. The exported symbols allow other GPL code to hook those initialization/quirk debug tracepoints when the xHCI trace infrastructure is built.

## Control Flow

There is no runtime control flow beyond module/object initialization by the kernel tracepoint machinery. Compile-time inclusion of `xhci-trace.h` with `CREATE_TRACE_POINTS` causes `TRACE_EVENT`/`DEFINE_EVENT` definitions to materialize storage and registration metadata for the events. Runtime trace emission occurs in other xHCI source files that call the generated `trace_xhci_*` helpers.

## State and Persistence Behavior

This file owns tracepoint definition state generated by the Linux tracing macros. Trace records persist only in the active tracing buffers configured by ftrace/perf/tracefs; there is no driver-private persistent state.

## Dependencies and Integration Points

The only direct source dependency is `"xhci-trace.h"`, which in turn depends on the kernel tracepoint framework and xHCI decoding helpers. Build-system integration must compile this file exactly once into the xHCI host driver objects so all tracepoint declarations have one definition provider.

## Risks and Edge Cases

The primary risk is tracepoint one-definition-rule breakage: defining `CREATE_TRACE_POINTS` in more than one xHCI object would create duplicate symbols, while omitting this file would leave tracepoints undefined. Exporting only `xhci_dbg_quirks` and `xhci_dbg_init` is intentional; adding exports changes module coupling and GPL symbol surface.

## Test Signals

Useful signals are successful xHCI host build/link with tracing enabled, presence of `xhci-hcd` trace events under tracefs, ability to enable `xhci_dbg_init` and `xhci_dbg_quirks`, and active trace output during xHCI initialization or quirk detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.h` declares the xHCI host controller tracepoint set. The source was read as a complete 652-line file. It defines reusable event classes and concrete events for formatted debug messages, context structures, TRBs, virtual devices, URBs, stream contexts, endpoint contexts, slot contexts, input-control contexts, rings, port status/control, doorbells, and xHCI debug capability requests. These tracepoints give maintainers low-overhead observability into xHCI scheduling, command handling, device setup, hub state, and DbC gadget activity.

## Important APIs, Types, and Functions

Trace systems are declared as `TRACE_SYSTEM xhci-hcd` and `TRACE_SYSTEM_VAR xhci_hcd`. Event classes include `xhci_log_msg`, `xhci_log_ctx`, `xhci_log_trb`, `xhci_log_free_virt_dev`, `xhci_log_virt_dev`, `xhci_log_urb`, `xhci_log_stream_ctx`, `xhci_log_ep_ctx`, `xhci_log_slot_ctx`, `xhci_log_ctrl_ctx`, `xhci_log_ring`, `xhci_log_portsc`, `xhci_log_doorbell`, and `xhci_dbc_log_request`.

Concrete tracepoints include `xhci_dbg_address`, `xhci_dbg_context_change`, `xhci_dbg_quirks`, `xhci_dbg_reset_ep`, `xhci_dbg_cancel_urb`, `xhci_dbg_init`, `xhci_dbg_ring_expansion`, `xhci_address_ctx`, `xhci_handle_event`, `xhci_handle_command`, `xhci_handle_transfer`, `xhci_queue_trb`, DbC TRB events, virtual-device allocation/setup/stop/free events, URB enqueue/giveback/dequeue events, stream context events, endpoint/slot/control context command events, ring allocation/free/expansion/enqueue/dequeue events, port status events, host/endpoint doorbells, and DbC request allocation/free/queue/giveback events.

The event payloads snapshot xHCI and USB types including `struct va_format`, `struct xhci_hcd`, `struct xhci_container_ctx`, `struct xhci_ring`, `struct xhci_generic_trb`, `struct xhci_virt_device`, `struct urb`, `struct xhci_stream_info`, `struct xhci_ep_ctx`, `struct xhci_slot_ctx`, `struct xhci_input_control_ctx`, `struct xhci_port`, and `struct dbc_request`.

## Control Flow

The header has compile-time trace declaration flow rather than normal function flow. It sets up a multi-read-safe include guard, includes tracepoint and xHCI/DbC definitions, declares event classes with `TP_PROTO`, `TP_ARGS`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`, then maps many concrete `DEFINE_EVENT` tracepoints onto those classes. The final block intentionally sits outside the guard, sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`, and includes `<trace/define_trace.h>` so the trace generator can produce definitions when included by `xhci-trace.c` with `CREATE_TRACE_POINTS`.

At runtime, callers elsewhere in the xHCI driver invoke generated `trace_xhci_*` functions. The tracepoint snapshots raw fields into trace entries and formats them through xHCI decoding helpers such as `xhci_decode_trb`, `xhci_decode_ep_context`, `xhci_decode_slot_context`, `xhci_decode_ctrl_ctx`, `xhci_decode_portsc`, `xhci_decode_doorbell`, and `xhci_ring_type_string`.

## State and Persistence Behavior

This header defines trace event schemas, not driver-owned persistent state. Runtime state is transient: each enabled event copies selected fields into kernel tracing buffers. The events deliberately record DMA addresses, virtual pointers, TRB words, port status words, URB lengths/status, ring enqueue/dequeue positions, context flags, and DbC request status at the moment of tracing, making later state changes irrelevant to the recorded entry.

## Dependencies and Integration Points

Direct dependencies are `<linux/tracepoint.h>`, `"xhci.h"`, and `"xhci-dbgcap.h"`. The file integrates with the Linux tracepoint/ftrace infrastructure, xHCI core decode helpers, USB core URB and endpoint helpers, and debug capability request structures. It is consumed by many xHCI implementation files through generated trace helpers, and by `xhci-trace.c` as the one definition unit.

## Risks and Edge Cases

Tracepoint payloads must avoid dereferencing invalid objects when callers pass partially initialized or teardown-path objects. Several events capture virtual pointers and DMA addresses; that is useful for debugging but sensitive in logs and only meaningful within the running kernel context. Formatting depends on decode helpers and buffer sizes such as `XHCI_MSG_MAX`; mismatches can reduce trace usefulness. The `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` placement is fragile and must remain outside the guard for trace generation. Schema changes affect user-space tracing scripts that parse xHCI trace events.

## Test Signals

Useful signals include successful xHCI build with tracing enabled, generated trace event files under tracefs for the `xhci-hcd` system, enabling TRB/URB/ring/port events during enumeration and transfer tests, DbC event coverage when debug capability support is active, and validation that decoded port/TRB/context strings match expected hardware state during command, transfer, suspend, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-trace.h -->
