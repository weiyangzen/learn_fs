<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.h

## Purpose
This private header declares endpoint lifecycle functions for the BDC driver.

## Important APIs, Types, And Functions
It declares `bdc_init_ep()` to create software endpoint objects, `bdc_ep_enable()` and `bdc_ep_disable()` to configure or tear down an endpoint, and `bdc_free_ep()` to free all endpoint structures.

## Control Flow
The declarations connect core/gadget initialization in `bdc_udc.c` with the endpoint implementation in `bdc_ep.c`.

## State And Persistence
The header has no state. The declared functions allocate/free endpoint objects, descriptor lists, queue state, and endpoint flags.

## Dependencies And Integration Points
It depends on `struct bdc` and `struct bdc_ep` from `bdc.h`, and on the USB gadget core through the implementation.

## Risks
The file comment incorrectly says it is a debug header. The interface is intentionally narrow; callers should not allocate BD lists or endpoint objects directly.

## Test Signals
Compile tests catch signature drift. Runtime validation comes from UDC init/exit, EP0 enable on startup/connect, and non-EP0 enable/disable through gadget function binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.h -->
