<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c` is the common Linux EHCI USB 2.0 host-controller implementation. It owns the generic `hc_driver` callbacks, controller reset/start/stop/shutdown, interrupt handling, URB dispatch, endpoint teardown/reset, PM helpers, module parameters, and initialization of platform driver variants that are compiled into the core. It includes `ehci-dbg.c`, `ehci-hub.c`, `ehci-mem.c`, `ehci-q.c`, `ehci-sched.c`, timer and sysfs code. The source was read as a complete 1401-line file.

## Important APIs, Types, and Functions

Important exported or shared functions include `ehci_handshake()`, `ehci_reset()`, `ehci_setup()`, `ehci_suspend()`, `ehci_resume()`, and `ehci_init_driver()`. Core lifecycle functions are `ehci_halt()`, `tdi_reset()`, `ehci_quiesce()`, `ehci_turn_off_all_ports()`, `ehci_silence_controller()`, `ehci_shutdown()`, `ehci_stop()`, `ehci_init()`, and `ehci_run()`. Runtime callbacks include `ehci_irq()`, `ehci_work()`, `ehci_urb_enqueue()`, `ehci_urb_dequeue()`, `ehci_endpoint_disable()`, `ehci_endpoint_reset()`, `ehci_get_frame()`, and `ehci_remove_device()`. Module parameters are `log2_irq_thresh`, `park`, and `ignore_oc`.

## Control Flow

`ehci_setup()` derives operational registers from capability length, caches structural parameters, initializes memory/schedule state, halts the controller, and resets it. `ehci_init()` initializes locks, hrtimer state, lists, periodic schedule size, DMA pools, async queue head, interrupt threshold, optional park mode, per-port-change support, scatter-gather capacity, and unlink bookkeeping. `ehci_run()` programs the periodic frame list and async head, configures 64-bit segment if advertised, starts `CMD_RUN`, sets the configured flag under the port-reset rwsem, waits for hardware running state, enables interrupts, and creates debugfs/sysfs files.

At runtime, URB enqueue builds qTD/QH transactions for control/bulk/interrupt, schedules interrupt QHs, or submits high-speed/full-speed isochronous transfers through ITD/SITD paths. The IRQ handler acknowledges status, handles normal/error completions by running `ehci_work()`, completes IAA unlink cycles, starts remote-wakeup port resume timers, polls root hub status for port changes, and handles fatal/controller-dead cases by stopping schedules and disabling interrupts. Stop/shutdown quiesce schedules, power off ports, clear configured flag, cancel timers, remove diagnostics, free ITDs, and clean DMA memory.

## State and Persistence Behavior

EHCI state is in `struct ehci_hcd`: command shadow, root-hub state, async/periodic schedules, DMA pools, timers, unlink lists, bandwidth tables, TT list, port bitmaps, reset timers, flags for hardware quirks, and debug/sysfs state. Hardware-visible state includes operational registers, frame list base, async head, configured flag, interrupt enables, port status, and endpoint schedule descriptors in coherent DMA memory. There is no file-backed persistence; resume can preserve hardware power or reset and mark root hub power lost.

## Dependencies and Integration Points

The file depends on the USB HCD core, PCI/platform support, DMA pools/coherent memory, debugfs, timers, OTG hooks, and `ehci.h` internal types. Platform wrappers copy `ehci_hc_driver` through `ehci_init_driver()` and override reset/port-power behavior or add private storage. It integrates with USB hub code via included `ehci-hub.c` and with transfer scheduling via included queue/scheduler code.

## Risks and Edge Cases

Controller lifecycle has many timing-sensitive handshakes; timeouts or all-ones reads indicate hardware removal or failure. The IRQ handler must avoid lost edge interrupts and controller-death races. QH unlink and completion can race with endpoint disable/dequeue and use guarded state transitions. Root-hub and companion-controller handover are sensitive to full/low-speed devices, integrated TT, and port-owner bits. Module parameters can change performance and overcurrent handling. PM resume must distinguish preserved power from hibernation/firmware takeover and can require full reset.

## Test Signals

Signals include successful high-speed enumeration, control/bulk/interrupt/isochronous URB traffic, unlink/dequeue stress, endpoint clear-halt, root-hub reset/suspend/resume, companion-controller handover for USB 1.1 devices, overcurrent handling with and without `ignore_oc`, fatal error handling, module load/unload, hibernation/system suspend, platform override behavior, and debugfs/sysfs creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c -->
