# subset-b-005517 Research

Grouped source research for the xHCI host-controller core/header and USB image-driver build metadata. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci.c` is the generic Linux xHCI host-controller implementation. It binds the USB core `hc_driver` contract to xHCI controller register programming, command-ring setup, event interrupter setup, URB queueing/cancellation, endpoint configuration, stream support, bandwidth accounting, device slot lifecycle, suspend/resume, USB2/USB3 link power management, hub updates, debugfs/DbC setup, and module init/exit. The source was read as a complete 5720-line file for this report.

## Important APIs, Types, and Functions

Public/exported entry points include `xhci_portsc_writel`, `xhci_portsc_readl`, `xhci_handshake`, `xhci_halt`, `xhci_start`, `xhci_reset`, `xhci_enable_interrupter`, `xhci_disable_interrupter`, `xhci_set_interrupter_moderation`, `xhci_run`, `xhci_stop`, `xhci_shutdown`, `xhci_suspend`, `xhci_resume`, `xhci_get_endpoint_index`, `xhci_add_endpoint`, `xhci_drop_endpoint`, `xhci_check_bandwidth`, `xhci_reset_bandwidth`, `xhci_stop_endpoint_sync`, `xhci_usb_endpoint_maxp`, `xhci_free_device_endpoint_resources`, `xhci_disable_slot`, `xhci_disable_and_free_slot`, `xhci_alloc_dev`, `xhci_find_raw_port_number`, `xhci_update_hub_device`, `xhci_gen_setup`, and `xhci_init_driver`.

Major internal helpers are grouped around controller setup (`xhci_init`, `xhci_run_finished`, `xhci_set_cmd_ring_deq`, `xhci_set_doorbell_ptr`, `xhci_hcd_page_size`, `xhci_zero_64b_regs`), power management (`xhci_save_registers`, `xhci_restore_registers`, `xhci_clear_command_ring`, `xhci_pending_portevent`, `xhci_disable_hub_port_wake`), URB DMA (`xhci_map_urb_for_dma`, `xhci_unmap_urb_for_dma`, temporary scatterlist bounce-buffer helpers, IDT eligibility), endpoint configuration (`xhci_configure_endpoint`, result decoders, resource reservations, endpoint reset/disable), stream setup (`xhci_alloc_streams`, `xhci_free_streams`), bandwidth accounting (`xhci_reserve_bandwidth`, interval table add/drop/check helpers), device setup/reset/free (`xhci_setup_device`, `xhci_discover_or_reset_device`, `xhci_free_dev`), and LPM (`xhci_change_max_exit_latency`, USB2 HIRD/BESL helpers, USB3 U1/U2 timeout calculation).

The file owns the generic `xhci_hc_driver` method table and copies it into platform-specific drivers through `xhci_init_driver()`, applying optional override hooks from `struct xhci_driver_overrides`.

## Control Flow

Initialization starts in `xhci_gen_setup()`: it caches capability/operational/runtime register pointers, reads controller capability fields, applies module and platform quirks, halts and resets the controller, chooses 32-bit or 64-bit DMA masks, initializes locks/work/completions, allocates controller memory with `xhci_mem_init()`, programs command/event/DCBAA/doorbell registers through `xhci_init()`, and configures either the USB2 or USB3 roothub side. `xhci_run()` then defers final hardware start until both roothubs are ready unless the controller has a single roothub; `xhci_run_finished()` enables interrupts/interrupter 0, starts the host, marks the command ring running, and handles NEC firmware command kickoff.

Normal I/O flows from USB core `urb_enqueue` into `xhci_urb_enqueue()`. The function allocates per-URB TD tracking, validates the addressed virtual device and endpoint state, rejects requests during stream or toggle transitions, and dispatches to control, bulk, interrupt, or isochronous ring-building helpers in the ring layer. Dequeue/cancel flows through `xhci_urb_dequeue()`, which validates unlink state, detects dead hardware, marks remaining TDs cancelled, and either lets pending stop/halt/dequeue handlers finish cleanup or queues a Stop Endpoint command and rings the command doorbell.

Configuration changes flow as `xhci_add_endpoint()` and `xhci_drop_endpoint()` edits to the input control context, followed by `xhci_check_bandwidth()`, which fixes the last valid context, submits Configure Endpoint, frees dropped/changed rings, installs new rings, and clears the input context. `xhci_configure_endpoint()` centralizes command submission, optional endpoint-limit reservation, optional software bandwidth reservation, doorbell ringing, completion wait, result decoding, and resource rollback/finalization.

Device lifecycle starts with `xhci_alloc_dev()` issuing Enable Slot, reserving control endpoint resources under quirks, allocating a virtual device, and storing `udev->slot_id`. `xhci_setup_device()` issues Address Device or context-only setup, handles transaction errors by disabling/reallocating the slot, and copies the hardware-assigned address back to USB core. Reset flows through `xhci_discover_or_reset_device()`, which may reallocate missing virtual devices after resume power loss, submits Reset Device, frees endpoint rings and stream info except ep0, clears bandwidth records, and updates TT activity. Free flows through `xhci_free_dev()`, `xhci_disable_slot()`, and `xhci_free_virt_device()`.

Suspend stops polling, disables unwanted port wake, marks hardware inaccessible, clears Run/Stop, waits for halt, clears command ring contents, saves registers, asks the controller to save state, and deletes compliance-mode timers. Resume either restores register state and restarts or performs a full halt/reset/reinitialization path when power was lost, suspend was broken, or `XHCI_RESET_ON_RESUME` is set. It then resumes DbC, checks pending port events, restarts compliance timers, re-enables port polling, and polls roothub status.

## State and Persistence Behavior

There is no file-backed persistence. Runtime state lives in `struct xhci_hcd`, virtual device records, endpoint rings, command/event rings, input/output contexts, roothub port structures, bandwidth tables, timers, work items, debugfs nodes, and hardware MMIO registers. Hardware-visible persistent state includes DCBAA, command ring pointer, event ring segment table/dequeue pointers, interrupter moderation/enables, device contexts, endpoint contexts, port wake/LPM bits, and max exit latency values. Suspend stores a minimal register snapshot in `xhci->s3` and per-interrupter `s3_*` fields, then restores them on resume if controller state survived.

The code uses `xhci->lock` for command, ring, endpoint, port, and state transitions that race with interrupts, and `xhci->mutex` for slot/address setup and primary/secondary HCD teardown coordination. Quirk flags in `xhci->quirks` permanently shape behavior for a controller instance after setup.

## Dependencies and Integration Points

Direct includes cover kernel timing, PCI/IOMMU/DMA, polling, IRQ, module parameters, DMI, USB sideband, and xHCI-local headers: `xhci.h`, `xhci-trace.h`, `xhci-debugfs.h`, and `xhci-dbgcap.h`. The implementation depends heavily on lower xHCI modules for memory allocation, ring/TRB queueing, event handling, hub control, debugfs, DbC, PCI quirks, sideband notifications, and port helpers.

Primary integration is the Linux USB HCD framework through `struct hc_driver`: IRQ handling, lifecycle, URB DMA, URB queue/dequeue, device slot allocation, endpoint add/drop/reset, bandwidth checks, streams, hub control, bus suspend/resume, device update, LPM timeout callbacks, and TT clear completion. It also integrates with platform/PCI glue through `xhci_init_driver()` override hooks and `xhci_get_quirks_t`.

## Risks and Edge Cases

High-risk areas are hardware handshakes and register ordering, especially reset/start/halt, suspend save/restore, posted MMIO writes, 64-bit register write ordering, and card removal returning all-ones. URB cancellation is concurrency-sensitive because rings may be reallocated while a TD is being cancelled, the endpoint may already be halted/stopped, or hardware may die during unlink. Endpoint/resource accounting has quirk-specific software limits and bandwidth tables that must roll back exactly on Configure Endpoint failure. Stream allocation rejects duplicate endpoints and pending URBs but has comments about missing dynamic reallocation and context cleanup details.

Power management has many controller-specific paths: broken suspend, reset-on-resume, compliance-mode polling, ASMedia flow-control modification, Renesas 64-bit register zeroing behind an IOMMU, spurious wake/reboot quirks, and USB3 delayed wake event detection. LPM timeout calculation is sensitive to endpoint service intervals, driver opt-out flags, hub tier policy, max exit latency width, and USB2 BESL/HIRD interpretation. Build-time `BUILD_BUG_ON()` layout checks are critical because many structures are hardware ABIs.

## Test Signals

Strong signals are successful kernel build with xHCI enabled, `BUILD_BUG_ON()` layout coverage at module init, USB2 and USB3 enumeration through root hubs, URB transfer tests for control/bulk/interrupt/isoc paths, cancellation/unlink stress, endpoint add/drop with alternate settings, software bandwidth failure/rollback tests, stream-capable mass-storage/UASP tests, suspend/resume and runtime PM across power-lost and state-preserved paths, hotplug/removal while transfers are active, LPM enable/disable with representative endpoint mixes, debugfs/DbC smoke tests, and hardware quirk regression coverage for Intel/AMD/NEC/ASMedia/Renesas/SNPS/Zhaoxin/Etron paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci.h` is the central private header for the Linux xHCI host-controller driver. It defines the controller MMIO register layouts, context structures, TRB/event encodings, ring and stream data structures, endpoint/device/roothub/interrupter/controller state containers, quirk flags, decode/debug helpers, inline conversion helpers, and cross-file prototypes used by `xhci.c`, ring code, memory code, hub code, trace/debugfs code, and bus-specific glue. The source was read as a complete 2613-line file for this report.

## Important APIs, Types, and Functions

Core hardware-facing types include `struct xhci_cap_regs`, `struct xhci_port_regs`, `struct xhci_op_regs`, `struct xhci_intr_reg`, `struct xhci_run_regs`, `struct xhci_doorbell_array`, `struct xhci_slot_ctx`, `struct xhci_ep_ctx`, `struct xhci_input_control_ctx`, `struct xhci_stream_ctx`, `union xhci_trb`, `struct xhci_erst_entry`, and `struct xhci_device_context_array`.

Software state types include `struct xhci_container_ctx`, `struct xhci_command`, `struct xhci_stream_info`, `struct xhci_bw_info`, `struct xhci_virt_ep`, `struct xhci_interval_bw_table`, `struct xhci_virt_device`, `struct xhci_root_port_bw_info`, `struct xhci_tt_bw_info`, `struct xhci_segment`, `struct xhci_td`, `struct xhci_ring`, `struct xhci_scratchpad`, `struct urb_priv`, `struct s3_save`, `struct xhci_bus_state`, `struct xhci_interrupter`, `struct xhci_port_cap`, `struct xhci_port`, `struct xhci_hub`, `struct xhci_hcd`, and `struct xhci_driver_overrides`.

Important macros encode xHCI register bits (`CMD_RUN`, `CMD_RESET`, `STS_HALT`, `STS_CNR`, `IMAN_IE`, `ERST_EHB`), context fields (`SLOT_FLAG`, `EP0_FLAG`, `LAST_CTX`, `ROOT_HUB_PORT`, `EP_TYPE`, `MAX_PACKET`, `TR_DEQ_PTR_MASK`), TRB fields and types (`TRB_NORMAL`, `TRB_SETUP`, `TRB_CONFIG_EP`, `TRB_TRANSFER`, `TRB_TYPE`, `TRB_CYCLE`, `TRB_CHAIN`, `TRB_IDT`, `TRB_TD_SIZE`), ring sizing (`TRBS_PER_SEGMENT`, `TRB_SEGMENT_SIZE`, `TRB_MAX_BUFF_SIZE`), completion codes (`COMP_SUCCESS`, `COMP_STALL_ERROR`, `COMP_COMMAND_ABORTED`, etc.), bandwidth constants, endpoint state bits, controller state bits, and a large quirk bitmap.

Inline helpers include HCD/controller conversion (`hcd_to_xhci`, `xhci_to_hcd`, `xhci_get_usb3_hcd`, `xhci_hcd_is_usb3`, `xhci_has_one_roothub`), 64-bit MMIO access (`xhci_read_64`, `xhci_write_64`), link TRB quirk selection, URB-to-transfer-ring lookup, IDT eligibility, and many trace/debug decoders for TRBs, control contexts, slot contexts, port status, USB status, doorbells, endpoint states, endpoint types, and endpoint contexts.

## Control Flow

This header does not own an independent runtime flow, but it defines the contracts that make the flow in `xhci.c` and companion files possible. The register structures map MMIO regions discovered during setup. Context structures are allocated by memory helpers, filled by setup/configuration helpers, and handed to hardware through command TRBs. Ring/TRB structures are manipulated by queueing and event handlers. State bits in `xhci_hcd`, `xhci_virt_ep`, and `xhci_virt_device` gate whether higher-level flows may touch hardware, queue URBs, clear toggles, allocate streams, or recover from port errors.

The prototype section connects the implementation units: memory/context helpers, ring queue helpers, command timeout handling, event interrupter management, roothub operations, power management, and generic HCD lifecycle methods. `xhci_driver_overrides` allows bus glue to replace selected methods while preserving the generic method table.

## State and Persistence Behavior

The header defines in-memory and hardware-visible state layouts. Hardware ABI state is persistent only while controller memory and MMIO programming remain valid: device contexts, endpoint contexts, stream contexts, TRBs, ERST entries, scratchpads, and register values must match xHCI layout and alignment requirements. Software state persists for the lifetime of the controller instance in `struct xhci_hcd`, for the lifetime of a USB device slot in `struct xhci_virt_device`, for endpoint configuration lifetimes in `struct xhci_virt_ep`, and for individual URBs in `struct urb_priv` and `struct xhci_td`.

No file-backed storage is defined. Suspend/resume state is represented in `struct s3_save` and interrupter `s3_*` fields. Debug decode helpers format state into caller-provided buffers and do not retain it.

## Dependencies and Integration Points

The header includes Linux USB/HCD, timer, kernel, bit, and 64-bit MMIO helpers plus xHCI-local capability, extended-capability, port, and PCI quirk headers. Its declarations integrate with `xhci-mem.c` for allocation and context manipulation, `xhci-ring.c` for TRB queueing/event processing, `xhci-hub.c` for roothub control and port state, `xhci.c` for generic HCD operations, debugfs/trace code for observability, bus glue for PCI/platform overrides, and USB core types such as `struct usb_hcd`, `struct usb_device`, `struct urb`, and endpoint descriptors.

## Risks and Edge Cases

The largest risk is ABI drift: hardware register/context/TRB structures must keep exact sizes, offsets, bit definitions, endian annotations, alignment, and write semantics. Incorrect bit masks can corrupt controller state, lose interrupts, misprogram endpoint rings, or misdecode completion events. State-bit combinations in endpoints and controller state are concurrency-sensitive because interrupt handlers, command completion, PM, and USB core callbacks share them. The quirk bitmap is broad and controller-specific; reusing, reordering, or misinterpreting bits can silently change behavior on unrelated hardware.

Debug decode helpers use fixed caller-provided buffers and `sprintf`/`snprintf`; callers must provide adequate buffer sizes. Several macros assume valid endpoint indices, slot IDs, intervals, and context flags. IDT eligibility intentionally excludes isochronous transfers despite possible spec support.

## Test Signals

Useful signals are allmodconfig/USB xHCI compile coverage, sparse/endian checking of `__le32`/`__le64` fields, module init layout assertions in `xhci.c`, trace/debug formatting smoke tests, ring and command tests that verify TRB field construction against expected bit encodings, endpoint index/address round-trip tests, suspend/resume register save/restore tests, and hardware enumeration/transfer coverage across controllers with different quirk combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/image/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/image/Kconfig` defines the kernel configuration menu entries for legacy USB imaging devices. It exposes options for the Mustek MDC800 digital camera driver and the Microtek X6USB scanner driver. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

The file defines the `USB_MDC800` tristate symbol with prompt `USB Mustek MDC800 Digital Camera support` and the `USB_MICROTEK` tristate symbol with prompt `Microtek X6USB scanner support`. `USB_MICROTEK` declares `depends on SCSI` because the scanner is presented through the SCSI generic layer. The file also emits the menu comment `USB Imaging devices`.

## Control Flow

There is no runtime control flow. During kernel configuration, selecting `y` builds the matching driver into the kernel, selecting `m` builds it as a loadable module, and leaving it unset omits it. The selected symbols are consumed by the adjacent Makefile to include `mdc800.o` or `microtek.o`.

## State and Persistence Behavior

The only persistent state is the generated kernel configuration value in `.config` and derived build artifacts. The help text documents runtime device-node expectations for the MDC800 (`/dev/mustek` with major 180 minor 32) and SCSI generic exposure for Microtek scanners, but this Kconfig file does not create devices or store runtime data.

## Dependencies and Integration Points

The file integrates with the Linux Kconfig system, `drivers/usb/image/Makefile`, the `mdc800` and `microtek` driver sources in the same directory, and the SCSI subsystem dependency for `USB_MICROTEK`. Userspace integration is documented for `gphoto` for MDC800 and SCSI generic scanner access for Microtek devices.

## Risks and Edge Cases

The options are for old hardware and user-facing help text names specific historical tools and manual device-node creation. If `USB_MICROTEK` were selectable without SCSI, builds or runtime scanner exposure would be broken, so the dependency is important. Kconfig symbol renames would need synchronized Makefile and documentation updates.

## Test Signals

Test signals are `make oldconfig/menuconfig` visibility checks, build coverage for `USB_MDC800=y/m`, build coverage for `USB_MICROTEK=y/m` with SCSI enabled, verification that `USB_MICROTEK` is hidden or unavailable when SCSI is disabled, and module-name checks for `mdc800` and `microtek`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/image/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/image/Makefile` is the kbuild makefile for USB image drivers. It maps Kconfig symbols to object files so the selected legacy camera/scanner drivers are built into the kernel or as modules. The source was read as a complete 7-line file for this report.

## Important APIs, Types, and Functions

The makefile has two kbuild object rules: `obj-$(CONFIG_USB_MDC800) += mdc800.o` and `obj-$(CONFIG_USB_MICROTEK) += microtek.o`. There are no functions or runtime types.

## Control Flow

There is no runtime flow. At build time, kbuild expands `obj-y` for built-in selections and `obj-m` for module selections. If the corresponding Kconfig symbol is unset, the object is not compiled from this directory.

## State and Persistence Behavior

The file does not own runtime state. Its outputs are build artifacts: built-in object linkage when selected as `y`, or loadable modules when selected as `m`. The state source is the configured value of `CONFIG_USB_MDC800` and `CONFIG_USB_MICROTEK`.

## Dependencies and Integration Points

This makefile depends on the Kconfig symbols defined in the sibling `Kconfig` and on the existence of `mdc800.c`/`microtek.c` sources that compile to `mdc800.o` and `microtek.o`. It integrates with the parent USB drivers build and the Linux kbuild `obj-*` mechanism.

## Risks and Edge Cases

The main risk is symbol/object drift: if a Kconfig symbol is renamed or a source file is moved, the object rule must change with it. Because `microtek` depends on SCSI at Kconfig level, the Makefile assumes that dependency filtering has already happened and does not restate it.

## Test Signals

Test signals are kernel builds with each symbol unset, built in, and modular; confirmation that `mdc800.o` and `microtek.o` appear only for selected configs; and module packaging checks that the expected `mdc800` and `microtek` modules are produced for `m` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/Makefile -->
