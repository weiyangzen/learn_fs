# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.c

## Purpose
`c67x00-hcd.c` implements the Linux USB host-controller-driver layer and root-hub behavior for one Cypress C67X00 SIE in host mode. It provides root hub status/control operations, HCD lifecycle hooks, frame-number retrieval, IRQ callback handling, and setup/teardown of the scheduler-backed HCD instance.

## Important APIs, Types, And Functions
- `c67x00_hub_des` is the fixed two-port hub descriptor.
- `c67x00_hub_status_data()` reports port connection-change bits to USB core.
- `c67x00_hub_control()` handles hub class requests such as `GetPortStatus`, `SetPortFeature RESET`, and clear-change operations.
- `c67x00_hcd_irq()` is called by common IRQ dispatch and kicks scheduling on TD-list-done or SOF/EOP events.
- `c67x00_hcd_start()`, `stop()`, and `get_frame()` implement `hc_driver` hooks.
- `c67x00_hc_driver` wires URB enqueue/dequeue, endpoint disable, frame number, and hub operations into USB core.
- `c67x00_hcd_probe()` allocates a `usb_hcd`, initializes `struct c67x00_hcd`, starts the scheduler, adds the HCD, and attaches the SIE IRQ callback.
- `c67x00_hcd_remove()` stops the scheduler, removes the HCD, and drops the HCD reference.

## Control Flow
HCD probe creates a USB 1.1 memory-mapped HCD, initializes lists for isochronous, interrupt, control, and bulk URBs, sets C67X00 internal TD/buffer base addresses by SIE number, initializes host ports, starts the scheduler, and registers the HCD with USB core. Hub requests read/write low-level USB status/control registers and perform port reset through HPI commands. IRQ callbacks kick the scheduler when TD lists complete or SOF/EOP occurs.

## State And Persistence Behavior
Runtime host state lives in `struct c67x00_hcd`: port speed bitmask, URB counts, per-pipe queues, TD list and bandwidth accounting, internal memory allocation cursors, scheduler work, endpoint-disable completion, and frame tracking. No persistent state exists.

## Dependencies And Integration Points
The file depends on USB HCD core, root-hub request definitions, low-level C67X00 accessors, and scheduler functions declared in `c67x00-hcd.h`. It integrates with `c67x00-drv.c` through `c67x00_hcd_probe/remove` and the SIE IRQ callback pointer.

## Risks And Edge Cases
The root hub models power as always enabled and has limited suspend/over-current behavior. Port index checks use `wIndex > C67X00_PORTS`, so callers must provide one-based hub port indices as expected by USB core. Unknown SIE message flags only warn. Scheduler correctness is external but central to all URB I/O. Removal assumes `sie->private_data` is valid for host-mode SIEs.

## Test Signals
Attach low-speed and full-speed devices and verify port status bits and `low_speed_ports`. Exercise hub reset, clear connection change, frame-number reads, SOF/EOP scheduling, and TD-list-done scheduling. Run USB core enumeration and disconnect tests for both ports. Validate HCD remove with active URBs.
