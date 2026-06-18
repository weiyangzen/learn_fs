<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.h

## Purpose
This private header declares the BDC command helpers implemented in `bdc_cmd.c`.

## Important APIs, Types, And Functions
It declares device command helpers (`bdc_address_device()`), endpoint configuration commands (`bdc_config_ep()`, `bdc_dconfig_ep()`), endpoint operation commands (`bdc_stop_ep()`, `bdc_ep_set_stall()`, `bdc_ep_clear_stall()`, `bdc_ep_bla()`), and remote/function wake commands (`bdc_function_wake()`, `bdc_function_wake_fh()`).

## Control Flow
The declarations let endpoint and gadget code issue hardware commands without exposing the lower-level command register polling functions.

## State And Persistence
This header has no state. The declared functions mutate BDC registers, endpoint flags, hardware endpoint configuration, and device address or wake state.

## Dependencies And Integration Points
It depends on `struct bdc`, `struct bdc_ep`, `u32`, and `dma_addr_t` definitions made available before inclusion, normally through `bdc.h`.

## Risks
The comment says "header for the BDC debug functions", which is stale and can mislead readers. The header intentionally exposes only command-level operations, so new code should not duplicate command register programming elsewhere.

## Test Signals
Compile tests catch declaration drift. Runtime validation comes from call sites in endpoint enable/disable, EP0 SET_ADDRESS, halt/clear-halt, dequeue, and remote wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.h -->
