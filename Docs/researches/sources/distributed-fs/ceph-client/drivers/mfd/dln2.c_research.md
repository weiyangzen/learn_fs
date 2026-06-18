# sources/distributed-fs/ceph-client/drivers/mfd/dln2.c

## Purpose
`dln2.c` is the USB MFD core for the Diolan DLN-2 adapter. It provides a request/response transport for child GPIO, I2C, SPI, and ADC drivers, demultiplexes asynchronous events, manages USB bulk URBs, and registers hotplug MFD children.

## Important APIs, Types, and Functions
`struct dln2_header` and `struct dln2_response` define the USB message protocol. `struct dln2_rx_context` and `struct dln2_mod_rx_slots` manage per-module response slots indexed by echo values. `struct dln2_dev` stores USB endpoints, URBs, slot pools, callback list, and disconnect state. Exported APIs are `dln2_transfer()`, `dln2_register_event_cb()`, and `dln2_unregister_event_cb()`. Key internals include `dln2_rx()`, `dln2_transfer_complete()`, `_dln2_transfer()`, `dln2_check_hw()`, `dln2_setup_rx_urbs()`, `dln2_stop()`, `dln2_probe()`, suspend, resume, and disconnect.

## Control Flow
Probe binds only interface 0, locates bulk endpoints, initializes wait queues, spinlocks, completions, event list, and RX URBs, submits the URB pool, verifies hardware ID and serial number through control transfers, then registers GPIO/I2C/SPI/ADC hotplug children with handle-specific platform data. Child transfers allocate a response slot, send a USB bulk message with the slot number in `echo`, wait up to 200 ms for the matching RX URB, validate protocol result, copy response data, free the slot, and resubmit the held URB. RX URBs either dispatch events by RCU callback list or complete a waiting transfer slot. Disconnect/suspend stop new transfers, complete waiters, wait for active transfers to drain, and kill URBs.

## State and Persistence
State is volatile and per USB interface: URB buffers, in-flight response contexts, event callbacks, active transfer count, and disconnect flag. No persistent storage exists. Child devices are removed on disconnect.

## Dependencies and Integration Points
The driver depends on USB bulk endpoints, platform MFD children, Linux completions/wait queues/spinlocks/RCU, and `linux/mfd/dln2.h` command definitions used by child drivers. ACPI ADR matching is provided for child functions.

## Risks and Edge Cases
`dln2_rx()` invokes event callbacks while holding `event_cb_lock` and inside an RCU read section; callbacks must not sleep or re-enter registration paths that need the same lock. `dln2_suspend()` calls `dln2_stop()` and sets `disconnect = true`; resume clears it and restarts URBs but does not rerun hardware init or recreate children. Late or malformed responses are dropped and logged. All request slots share a short 200 ms timeout, which may be tight on slow USB paths.

## Test Signals
Test concurrent transfers per handle up to 16 slots, timeout and late-response behavior, disconnect while transfers are active, event callback register/unregister races, suspend/resume transfer recovery, hardware ID rejection, serial-number logging, and child driver transfers through GPIO/I2C/SPI/ADC handles.
