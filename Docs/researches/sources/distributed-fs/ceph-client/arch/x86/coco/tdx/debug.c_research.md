# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/debug.c

## Purpose
Initialization-time debug reporting for TDX TD attributes and TD controls. It translates known metadata bits into names for boot logs.

## Important APIs, Types, And Functions
`tdx_dump_attributes()` prints recognized `TDX_TD_ATTR_*` bits and any unknown remainder. `tdx_dump_td_ctls()` prints recognized `TD_CTLS_*` bits and unknown remainder. Static string tables are indexed by bit number using `DEF_TDX_TD_ATTR_NAME()` and `DEF_TD_CTLS_NAME()`.

## Control Flow And State
Both functions iterate over sparse name arrays, print names for set known bits, clear consumed bits from the local copy, and print a hex unknown mask for remaining bits. State is read-only `__initdata`; there is no persistence after init.

## Dependencies And Integration
Depends on `<asm/tdx.h>` bit definitions and printk. `tdx_announce()` in `tdx.c` invokes these helpers after `TDG_VP_INFO` and `TDCS_TD_CTLS` reads.

## Risks And Test Signals
Risks are stale bit names, array indexes that no longer match architecture definitions, and misleading unknown masks. Signals are TDX guest boot logs on debug and non-debug TDs, plus compile failures when TDX bit definitions change.
