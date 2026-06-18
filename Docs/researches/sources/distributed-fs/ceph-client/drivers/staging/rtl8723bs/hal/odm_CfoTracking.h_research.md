# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.h

## Purpose

`odm_CfoTracking.h` declares CFO tracking thresholds, state, and public APIs. The source was read as a complete 39-line file.

## Important APIs, Types, and Functions

It defines `CFO_TH_XTAL_HIGH`, `CFO_TH_XTAL_LOW`, `CFO_TH_ATC`, `struct cfo_tracking`, and prototypes for `ODM_CfoTrackingReset`, `ODM_CfoTrackingInit`, `ODM_CfoTracking`, and `odm_parsing_cfo`.

## Control Flow

The header contains no runtime flow; it provides the declarations consumed by `odm.c`, `odm_CfoTracking.c`, and PHY status parsing.

## State and Persistence Behavior

`struct cfo_tracking` persists inside `dm_odm_t` and stores ATC status, crystal cap, CFO tails, previous average, packet counters, and reset/force flags.

## Dependencies and Integration Points

It depends on standard driver boolean and integer typedefs made available through ODM includes. It integrates with the ODM watchdog and PHY status parser.

## Risks and Edge Cases

The `ODM_CfoTrackingReset` prototype is split oddly over two lines but compiles as a normal declaration. Some fields (`bForceXtalCap`, `bReset`) are declared but not used in the visible implementation.

## Test Signals

Compile coverage and state initialization checks in `ODM_CfoTrackingInit`/reset are the main signals.
