# `sources/distributed-fs/ceph-client/include/linux/usb/hcd.h`

## Purpose

`hcd.h` is the internal USB host-controller-driver contract used by usbcore and HCD implementations. It defines host controller state, host-driver callback vectors, URB enqueue/unlink/giveback helpers, DMA buffer pools, root hub support, transaction translator state, bandwidth calculations, monitor hooks, PCI/platform integration, and shared host-side enumeration utilities.

## Important APIs, Types, and Constants

- USB PID constants and hub request macros describe protocol-level values used by host controller and hub code.
- `struct usb_hcd` embeds `struct usb_bus`, reference counts, root hub polling/work state, driver hooks, PHY links, atomic flags, authorization defaults, MSI state, DMA pools, controller state, shared-HCD pointers, local memory pool, and controller-private tail storage.
- `struct hc_driver` is the HCD vtable: reset/start/stop/shutdown, IRQ, URB enqueue/dequeue, DMA mapping override, endpoint disable/reset, root hub control, suspend/resume, stream management, bandwidth management, address/enable/update/reset device, link power management, port power, and EH test-mode support.
- HCD flags describe memory/DMA/shared hardware and USB speed generation; runtime flags track hardware accessibility, root-hub polling, wakeup, dead state, authorization defaults, and deferred root hub registration.
- URB and endpoint helpers include `usb_hcd_link_urb_to_ep()`, unlink checks, submit/unlink/giveback, DMA map/unmap, endpoint flush/disable/reset, unlink synchronization, bandwidth allocation, frame number, and toggle macros.
- Creation and teardown APIs include `usb_create_hcd()`, `usb_create_shared_hcd()`, `usb_get_hcd()`, `usb_put_hcd()`, `usb_add_hcd()`, `usb_remove_hcd()`, PCI probe/remove/shutdown, and platform shutdown.
- Root hub/TT support includes `struct usb_tt`, `struct usb_tt_clear`, `usb_hub_clear_tt_buffer()`, hub class requests, `usb_calc_bus_time()`, power-management helpers, usbmon operations, and global usbcore IDR/kill queues.

## Control Flow and Lifetimes

An HCD driver allocates an HCD object, fills `hc_driver`, maps resources, initializes PHY/power, adds the HCD, and registers the root hub. usbcore submits URBs through `usb_hcd_submit_urb()`, which maps buffers, links URBs to endpoints, and calls `hc_driver->urb_enqueue()`. Completion flows back through the HCD, `usb_hcd_giveback_urb()`, optional BH work, usbmon hooks, and client completion callbacks. Unlink paths validate status with `usb_hcd_check_unlink_urb()`, call driver dequeue hooks, unlink from endpoint lists, and synchronize before endpoint teardown. Removal stops root hub polling, disables endpoints, tears down DMA pools, unmaps resources, and drops HCD references.

## State and Persistence Behavior

Runtime state includes root hub timer/status URB, controller flags, authorization policy, controller state machine, DMA pools, endpoint queues, bandwidth schedule, transaction translator clear work, and shared primary/secondary HCD relationships. No disk persistence exists. Concurrency is central: flags use atomic bit operations, URB lists use endpoint locks in implementation, giveback BH has spinlock-protected lists, bandwidth and address0 paths use mutexes, and usbcore globals use IDR locks and wait queues.

## Dependencies and Integration Points

The header depends on usbcore data structures, Linux interrupt, IDR, rwsem, DMA pool, gen_pool, PM, PCI, platform, PHY, hub Chapter 11 definitions, and optional usbmon. It is consumed by EHCI/OHCI/UHCI/xHCI and platform HCD glue, hub enumeration code, USB monitor, power-management paths, and PHY/OTG integration.

## Risks and Edge Cases

URB lifetime races are the main risk: completion, unlink, endpoint disable, and device disconnect can all converge. Shared HCDs must preserve primary/secondary ownership and resource teardown ordering. DMA mapping overrides must match unmapping and handle setup packets. Root hub polling flags can miss wakeups if not synchronized. Bandwidth callbacks must follow add/drop/check/reset sequencing. PCI AMD wakeup quirks and controller-dead handling are hardware-specific failure paths.

## Test Signals

Run builds for multiple HCDs and `CONFIG_USB_PCI`, `CONFIG_PM`, `CONFIG_USB_MON`, and `CONFIG_USB_HCD_TEST_MODE` combinations. Exercise device enumeration, disconnect during URB traffic, URB unlink storms, endpoint disable/reset, suspend/resume, root hub wakeup, transaction translator clear-buffer recovery, bandwidth-heavy isochronous endpoints, shared xHCI HCDs, DMA mapping debug, usbmon traces, and HCD remove/reprobe cycles.
