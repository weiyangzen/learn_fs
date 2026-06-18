# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.h

## Purpose
`c67x00-hcd.h` defines the Cypress C67X00 host-controller private state, bandwidth constants, HCD conversion helpers, and cross-file prototypes for HCD setup and transfer scheduling.

## Important APIs, Types, And Functions
- Bandwidth constants define `TOTAL_FRAME_BW`, `DEFAULT_EOT`, standard and isochronous max frame bandwidth, and periodic bandwidth policy.
- `struct c67x00_hcd` stores the SIE pointer, port speed state, URB counts, per-pipe lists, bandwidth accounting, TD/buffer memory allocation cursors, scheduler work, endpoint-disable completion, and frame numbers.
- `hcd_to_c67x00_hcd()` and `c67x00_hcd_to_hcd()` convert between USB core HCD and private data.
- Prototypes expose `c67x00_hcd_probe/remove`, URB enqueue/dequeue, endpoint disable, scheduler kick/start/stop.
- `c67x00_hcd_dev()` returns the controller device for logging.

## Control Flow
The header has no executable control flow. It defines the shared contract between `c67x00-hcd.c`, the scheduler implementation, and the platform driver. Compile-time assertion checks that USB pipe constants range from 0 to 3 because the private state uses a four-entry pipe list indexed by pipe type.

## State And Persistence Behavior
All defined state is in-memory HCD state for one host-mode SIE. Bandwidth constants influence scheduler behavior but are not runtime-persistent.

## Dependencies And Integration Points
It includes USB HCD core headers and local `c67x00.h`. It is included by platform and HCD implementation files and must match scheduler expectations for TD memory and queue layout.

## Risks And Edge Cases
Bandwidth constants are tuning-sensitive and can trade bulk throughput against isochronous deadlines. The pipe-index assumption is enforced at compile time but would break if USB core pipe constants changed. TD/buffer address fields are 16-bit and tied to C67X00 internal memory limits.

## Test Signals
Compile with scheduler files to validate prototypes and pipe assertion. Stress isochronous and bulk transfers to verify bandwidth tuning. Use endpoint-disable tests to confirm completion behavior and queue cleanup.
