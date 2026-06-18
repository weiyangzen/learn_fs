# sources/distributed-fs/ceph-client/drivers/of/unittest-data/Makefile

## Purpose
Builds DTBO fixtures and static overlay-application DTBs for OF self-tests.

## Important APIs, types, and functions
Uses Kbuild variables `obj-y`, `obj-$(CONFIG_OF_OVERLAY)`, `DTC_FLAGS_*`, `dtb-$(CONFIG_OF_OVERLAY)`, and `*-dtbs` composite DTB lists.

## Control flow
Always builds `testcases.dtbo.o`; with overlays enabled, builds overlay fixtures, enables `-@` for symbols, suppresses warnings for intentional malformed test inputs, and defines static tests using `fdtoverlay` over base DTBs.

## State and persistence behavior
Creates build artifacts and linker symbols consumed by `unittest.c`; no runtime logic exists here.

## Dependencies and integration points
Depends on Kbuild DTB rules, dtc, fdtoverlay, and fixture names declared in `unittest.c`.

## Risks and edge cases
Fixture lists must stay synchronized with `OVERLAY_INFO_EXTERN()` declarations. Removing `-@` breaks symbol/fixup tests. Bad overlays are intentionally excluded from static success composites.

## Test signals
Static composite DTBs provide build-time overlay validation; DTBO objects provide runtime unittest data.
