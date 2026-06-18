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
