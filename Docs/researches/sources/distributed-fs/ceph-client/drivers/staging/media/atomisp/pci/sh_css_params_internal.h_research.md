# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params_internal.h

## Purpose
Provides the minimal internal parameter-maintenance declaration for AtomISP CSS.

## Important APIs, Types, and Functions
Declares `sh_css_param_clear_param_sets()`, an internal routine used to clear or invalidate accumulated CSS parameter sets.

## Control Flow
No execution exists in this header. Callers include it when they need to reset parameter-set state outside the public `sh_css_params.h` contract.

## State and Persistence Behavior
The declared function implies global or shared parameter-set state owned elsewhere. Its safety depends on being called at pipeline teardown, reset, or configuration boundaries where stale parameter data must not leak into a later frame.

## Dependencies and Integration Points
No include dependencies beyond its guard. It is intentionally narrow to avoid exposing the full parameter struct internals to every user.

## Risks
Because the function has no parameters, it likely operates on hidden global state. Calling it while a pipeline is active could race with per-frame parameter upload or invalidate expected state.

## Test Signals
Reset/reconfigure tests should verify that old ISP parameter values are not reused after this routine is called and that active streaming paths are not disturbed by inappropriate clears.
