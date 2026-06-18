# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.h

## Purpose

`odm_EdcaTurboCheck.h` declares EDCA turbo state and APIs. The source was read as a complete 23-line file.

## Important APIs, Types, and Functions

It defines `struct edca_t` with current turbo state, current RDL state, and previous traffic index. It declares `odm_EdcaTurboCheck`, `ODM_EdcaTurboInit`, and `odm_EdcaTurboCheckCE`.

## Control Flow

There is no runtime flow.

## State and Persistence Behavior

The state persists inside `dm_odm_t->DM_EDCA_Table` and controls whether EDCA settings need to be restored.

## Dependencies and Integration Points

It is included by `odm.h` and used by the ODM watchdog.

## Risks and Edge Cases

Only a small subset of intended EDCA state is represented here; correctness depends on external traffic/non-BE tracking.

## Test Signals

Compile coverage and initialization checks after `ODM_EdcaTurboInit` are the main signals.
