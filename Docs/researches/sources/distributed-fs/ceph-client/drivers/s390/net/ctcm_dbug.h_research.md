# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.h

## Purpose
`ctcm_dbug.h` defines the CTCM debug-facility interface, debug levels, debug area IDs, metadata structure, function prototypes, and convenience macros used by the CTCM and MPC network driver code.

## Important APIs, Types, And Functions
It defines compile-time flags `do_debug`, `do_debug_ccw`, and `do_debug_data` from `DEBUG`, `DEBUGCCW`, and `DEBUGDATA`. Debug levels mirror kernel severity levels from `CTC_DBF_ALWAYS` through `CTC_DBF_DEBUG`. `enum ctcm_dbf_names` names six debug areas and `struct ctcm_dbf_info` describes each area. Prototypes expose registration, unregistration, and printf-style long text logging. Macros include `CTCM_DBF_TEXT`, `CTCM_DBF_HEX`, `CTCM_DBF_TEXT_`, `CTCM_DBF_DEV_NAME`, `MPC_DBF_DEV_NAME`, `CTCMY_DBF_DEV_NAME`, `CTCM_DBF_DEV`, `MPC_DBF_DEV`, and `CTCMY_DBF_DEV`.

## Control Flow
The macros dispatch directly to debug-facility calls or `ctcm_dbf_longtext()`. `CTCMY_*` macros branch on `IS_MPCDEV(dev)` to choose MPC or non-MPC debug areas. `strtail()` shortens function names for compact logs.

## State And Persistence
The header declares the external `ctcm_dbf` array populated by `ctcm_dbug.c`. It defines no persistent state.

## Dependencies And Integration Points
It depends on `asm/debug.h` and on external CTCM driver context for `IS_MPCDEV()` and valid `net_device` names/pointers in macros. It is the logging surface used throughout the CTCM driver.

## Risks And Test Signals
Risks include macro arguments with side effects, use before debug areas are registered, dependency on `IS_MPCDEV()` being visible at expansion sites, and fixed-size function-name/log formatting. Test signals include compile coverage across debug flag combinations, CTCM and MPC logging call sites, and debug output routing to the expected area.
