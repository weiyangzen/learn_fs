# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-drv.c

## Purpose
`c67x00-drv.c` is the platform-driver and common interrupt infrastructure for Cypress C67X00 USB controllers. It maps the Host Port Interface registers, initializes low-level hardware access, resets the controller, creates per-SIE subdrivers, and dispatches controller interrupts to each SIE.

## Important APIs, Types, And Functions
- `c67x00_probe_sie()` initializes a `struct c67x00_sie`, reads platform SIE mode, and calls `c67x00_hcd_probe()` for host mode.
- `c67x00_remove_sie()` removes host-mode SIEs.
- `c67x00_irq()` reads HPI status, acknowledges low-level IRQ state, fetches SIE messages, calls each SIE IRQ callback, and loops up to a bounded count.
- `c67x00_drv_probe()` obtains MEM and IRQ resources, platform data, maps HPI registers, initializes HPI locks and low-level registers, requests IRQ, resets hardware, and probes both SIEs.
- `c67x00_drv_remove()` removes SIEs, frees IRQ, unmaps HPI, releases memory, and frees the device.

## Control Flow
Platform probe requires one memory resource, one IRQ resource, and platform data. It reserves and maps HPI registers, initializes low-level communication, registers the IRQ handler, resets the device, then iterates over the two SIEs and starts host-controller support for those configured as host. IRQ handling reads status and repeatedly drains pending conditions: low-level mailbox completion, SIE messages, and SIE-specific callbacks. Removal reverses SIE creation before releasing common resources.

## State And Persistence Behavior
`struct c67x00_device` owns HPI base address, regstep, locks, platform data, platform device pointer, and two SIE states. Each SIE stores mode, lock, private host data, and IRQ callback. No persistent storage exists.

## Dependencies And Integration Points
The file depends on platform-device resources, platform data from `<linux/usb/c67x00.h>`, low-level HPI functions in `c67x00-ll-hpi.c`, and host-controller creation in `c67x00-hcd.c`. It is the bridge between board description and USB HCD registration.

## Risks And Edge Cases
The IRQ loop is capped and warns if status remains, which can indicate unhandled interrupt sources. Only host mode is supported; device/OTG modes report unsupported. Platform data is mandatory. Probe uses manual allocation/resource management, so failure ordering must stay correct. The IRQ is requested before reset, requiring low-level state to be ready.

## Test Signals
Instantiate a platform device with valid resources and SIE host configuration. Verify HPI mapping, reset success, two SIE mode paths, IRQ dispatch on SIE messages and SOF/EOP, and bounded-loop warning under forced stuck status. Remove while USB devices are attached to exercise HCD teardown first.
