# sources/distributed-fs/ceph-client/drivers/extcon/extcon-fsa9480.c

## Purpose
`extcon-fsa9480.c` supports Fairchild FSA9480-compatible microUSB switch/accessory detector chips over I2C, reporting USB, host, charger, line-out, video-out, and jig extcon states.

## Important APIs, types, and functions
`struct fsa9480_usbsw` stores device, regmap, extcon device, and cached device bitmask. `cable_types[]` maps hardware device-type bits to extcon cables. `fsa9480_detect_dev()` reads device-type registers and reports attach/detach deltas. `fsa9480_irq_handler()` clears interrupt registers and triggers detection. Probe initializes regmap, timing, automatic switching, interrupt masks, wakeup, and initial detection.

## Control flow
Probe requires an I2C IRQ, registers an extcon device, initializes an 8-bit regmap, sets ADC detect time to 500 ms, configures automatic switching, unmasks attach/detach interrupts, requests a falling-edge threaded IRQ, enables wakeup, and runs detection. On IRQ, it bulk-reads INT1/INT2 to clear latched interrupts and, if nonzero, reads DEV_T1/DEV_T2. It clears extcon states no longer present before setting newly attached states and updates the cached bitmask.

## State and persistence behavior
Runtime state is the cached 16-bit cable/device mask and hardware register configuration. No persistent state exists.

## Dependencies and integration points
The driver depends on I2C, regmap, extcon provider APIs, IRQs, wakeup support, and OF/I2C IDs for FSA9480/FSA880/TSU6111-compatible devices.

## Risks and edge cases
The device-type bit macros are ordinal bit numbers, and `cable_types[]` indexes them directly; incorrect definitions would misreport cables. The volatile register callback marks `INT1_MASK`, not the interrupt status registers, which is suspicious for caching behavior. Read failures in detection leave cached state unchanged. The driver reports multiple extcon cables per hardware type, so consumers must handle composite states.

## Test signals
Attach/detach each supported accessory type, multi-cable mappings, interrupt clear behavior, I2C/regmap read failures, wakeup suspend/resume, compatible variants, and initial detection on a cable already inserted.
