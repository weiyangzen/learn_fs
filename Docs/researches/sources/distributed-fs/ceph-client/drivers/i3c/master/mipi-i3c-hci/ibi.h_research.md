# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ibi.h

## Purpose

`ibi.h` defines HCI In-Band Interrupt status descriptor bits and provides a helper to map an IBI target address to a Linux I3C device descriptor.

## Important APIs, Types, and Functions

- `IBI_STS`, `IBI_ERROR`, `IBI_STATUS_TYPE`, `IBI_HW_CONTEXT`, `IBI_TS`, `IBI_LAST_STATUS`, `IBI_CHUNKS`, `IBI_ID`, `IBI_TARGET_ADDR`, `IBI_TARGET_RNW`, and `IBI_DATA_LENGTH` decode IBI status words.
- `i3c_hci_addr_to_dev()` iterates the current I3C bus and returns the device whose dynamic address matches the supplied address.

## Control Flow

PIO and DMA IBI handlers decode target addresses from IBI status descriptors, call `i3c_hci_addr_to_dev()`, then use the returned descriptor to allocate/queue generic IBI slots or drop unknown-device interrupts.

## State and Persistence Behavior

The helper reads the current I3C bus device list and stores no state. It depends on device dynamic addresses being current after DAA or reattach.

## Dependencies and Integration Points

It depends on the Linux I3C bus iteration macros and `struct i3c_hci`. It is included by both PIO and DMA backend implementations.

## Risks and Edge Cases

Lookup is linear across bus devices. If an IBI arrives while device attach/detach or address change is in progress, higher-level locking must keep the bus list stable. Unknown addresses are normal for stale or rejected IBIs and must be handled by callers.

## Test Signals

IBI tests should cover known device lookup, unknown address drops, address changes after DAA, and both payload and no-payload IBI status decoding.
