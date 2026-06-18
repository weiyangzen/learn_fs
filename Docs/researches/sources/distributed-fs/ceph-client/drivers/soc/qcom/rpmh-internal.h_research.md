# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-internal.h

## Purpose

`rpmh-internal.h` is the private contract between the Qualcomm RPMh client layer (`rpmh.c`) and Resource State Coordinator driver (`rpmh-rsc.c`). It defines TCS sizing, controller/request state, and internal function prototypes.

## Important APIs, Types, and Functions

Constants define four TCS types, at most 16 commands per TCS, at most three TCSes per type, and derived slot counts. `struct tcs_group` describes one TCS group, including type, mask, offset, command slots, and active request pointers. `struct rpmh_request` wraps a `tcs_request`, inline command storage, optional completion, device, and free flag. `struct rpmh_ctrlr` stores cached sleep/wake requests and dirty state. `struct rsc_drv` stores MMIO bases, version, TCS groups, locks, waitqueue, PM notifiers, and embedded RPMh client state.

## Control Flow

The header declares the cross-file flow: `rpmh.c` sends active requests with `rpmh_rsc_send_data()`, writes sleep/wake control data with `rpmh_rsc_write_ctrl_data()`, invalidates TCS slots with `rpmh_rsc_invalidate()`, asks RSC to write next wakeup, and receives completion via `rpmh_tx_done()`. `rpmh-rsc.c` calls `rpmh_flush()` during low-power transitions.

## State and Persistence Behavior

All state is volatile kernel state reflecting RPMh hardware programming. Cached requests in `rpmh_ctrlr` persist for the life of an RSC controller and are flushed into sleep/wake TCS hardware before low-power entry. TCS register contents persist until invalidated, overwritten, or reset.

## Dependencies and Integration Points

It depends on bitmap helpers, waitqueues, and `<soc/qcom/tcs.h>`. It is not a public API; external clients use `<soc/qcom/rpmh.h>` while this header coordinates private implementation details.

## Risks and Edge Cases

The lock-order comment is important: `rsc_drv.lock` before `rpmh_ctrlr.cache_lock`. Violating it can deadlock PM flush and active transfer paths. Array sizes (`MAX_TCS_PER_TYPE`, `MAX_RPMH_PAYLOAD`) must remain consistent with hardware and public TCS definitions. `slots` is only valid for sleep/wake TCSes, while `req[]` is only for active transfers.

## Test Signals

Compile tests should catch structure drift across `rpmh.c` and `rpmh-rsc.c`. Runtime tests should stress active transfers, borrowed wake TCSes, sleep/wake cache flush, dirty-cache handling, PM callbacks, and lockdep for documented lock ordering.
