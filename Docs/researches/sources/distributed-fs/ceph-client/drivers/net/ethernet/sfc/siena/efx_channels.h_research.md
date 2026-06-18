# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.h

## Purpose
Declares Siena channel, interrupt, event queue, and NAPI management APIs.

## Important APIs
Exposes interrupt mode/RSS CPU globals, interrupt probe/remove/enable/disable, affinity functions, event queue start/stop, channel realloc/init/probe/set/remove/fini/start/stop, NAPI init/fini, and a dummy channel operation.

## Control flow and integration
`efx.c` uses the APIs during PCI lifecycle. `efx_common.c` starts/stops channels during datapath and reset flows. Ettool ring settings call channel reallocation. Self-tests use event queue start/stop behavior.

## State and persistence behavior
No state is stored in the header; implementations mutate `struct efx_nic` and `struct efx_channel`.

## Dependencies
Depends on core driver types from `net_driver.h` through users. Declarations must match `efx_channels.c`.

## Risks
Lifecycle ordering is critical: probe before enable, NAPI before event queue start, stop before remove. Misordered calls race with IRQ/NAPI paths.

## Test signals
Build checks plus interface open/close, reset, ring resize, and interrupt self-tests.
