# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.c

## Purpose
`uhci-hcd.c` is the shared core of the Linux UHCI USB 1.1 host-controller driver. It owns controller lifecycle, root-hub power-management state, interrupt handling, schedule allocation, debug initialization, module registration, and inclusion of the UHCI debug, queue, hub, and bus-glue implementation files.

## Important APIs, Types, And Functions
The file exposes shared operations consumed by bus glue through `struct hc_driver` instances: `uhci_start()`, `uhci_stop()`, `uhci_irq()`, `uhci_rh_suspend()`, `uhci_rh_resume()`, `uhci_hcd_endpoint_disable()`, `uhci_hcd_get_frame_number()`, and `uhci_count_ports()`. `finish_reset()`, `uhci_hc_died()`, `check_and_reset_hc()`, and generic non-PCI reset helpers handle hardware reset state. `configure_hc()` programs frame length, frame-list base, frame number, and optional bus-specific setup. `suspend_rh()`, `start_rh()`, and `wakeup_rh()` manage root-hub state transitions. Module init creates debugfs/cache state and registers platform and/or PCI drivers depending on configuration.

## Control Flow
At compile time this file includes `uhci-debug.c`, `uhci-q.c`, `uhci-hub.c`, and one or more bus glue files. Module init rejects `usb_disabled()`, allocates the `urb_priv` slab cache, creates debugfs root when applicable, registers platform glue first and PCI glue second. HCD start allocates the 1024-entry frame list, CPU-side ISO frame pointers, TD/QH DMA pools, terminating TD, skeleton QHs, and initializes hardware frame entries. It then configures the HC, marks state initialized, and starts the root hub. IRQ handling acknowledges UHCI status, detects fatal hardware errors, handles resume-detect by polling the root hub, and otherwise scans the schedule. Stop kills the controller, scans remaining work, synchronizes IRQs, deletes timers, and releases DMA/debug resources.

## State And Persistence Behavior
The core maintains all persistent runtime state in `struct uhci_hcd`: frame list DMA, skeleton QHs, TD/QH pools, root-hub state, frame counters, FSBR flags, quirk flags, port resume bitmaps, load accounting, wait queues, clocks/resets from platform glue, and function pointers supplied by bus glue. No state persists across unload or reset. `frame_number` expands the 10/11-bit hardware frame counter by requiring periodic polling.

## Dependencies And Integration Points
The file integrates with usbcore HCD APIs, DMA pools, coherent DMA allocation, debugfs, timers, PCI/platform bus glue, root-hub polling, and PM. The bus glue must supply register mapping, root-port count, reset/check/config callbacks, and quirks. Queue and hub logic are included into the same translation unit so static helpers can be shared.

## Risks And Edge Cases
UHCI hardware has multiple quirks: persistent HCH status, old Intel QH advancement bugs handled in `uhci-q.c`, overcurrent/resume-detect issues, ASpeed stale status, and controllers that lose state across suspend/hibernate. `suspend_rh()` must balance remote-wakeup policy against broken EGSM/RD behavior and may force root-hub polling. Resource unwinding in `uhci_start()` is multi-stage and depends on DMA pool/frame allocation order. `uhci_count_ports()` probes ambiguous registers and clamps impossible counts.

## Test Signals
Build all configured glue combinations: PCI-only, platform, GRLIB, and non-PCI support. Runtime tests should cover enumeration, control/bulk/interrupt/ISO traffic, suspend/resume with and without wakeup, controller halt error handling, endpoint disable waiting, port-count detection, debugfs creation/removal, and module load/unload without DMA leaks.
