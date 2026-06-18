
# sources/distributed-fs/ceph-client/drivers/soc/loongson/Makefile

## Purpose
Builds Loongson-2 GUTS and PM drivers according to Kconfig.

## Important APIs, Types, and Functions
No runtime APIs. Rules build `loongson2_guts.o` for `CONFIG_LOONGSON2_GUTS` and `loongson2_pm.o` for `CONFIG_LOONGSON2_PM`.

## Control Flow
Build includes objects according to selected symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes Loongson Kconfig symbols.

## Risks
Low build-rule risk; GUTS and PM functions are independent but both target Loongson-2 platforms.

## Test Signals
Build matrix for GUTS module/built-in and PM built-in.
