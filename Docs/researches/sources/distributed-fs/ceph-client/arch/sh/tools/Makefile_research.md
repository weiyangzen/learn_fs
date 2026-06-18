<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/tools/Makefile

## Purpose
This small Kbuild makefile wires SuperH generated-header tooling into the kernel build.

## Important APIs, Types, and Functions
It declares the generated target `include/generated/machtypes.h`, marks it under `targets`, and defines the rule that runs `arch/sh/tools/gen-mach-types` over `arch/sh/tools/mach-types`.

## Control Flow
When `archheaders` or dependent generated headers are requested, Kbuild invokes the awk generator and writes the generated machine-type header. The rule is purely build-time.

## State and Persistence Behavior
It persists only a generated header under `include/generated`. No runtime state exists.

## Dependencies and Integration Points
It depends on Kbuild variables such as `src`, `obj`, `targets`, and `quiet_cmd`/`cmd`, plus the companion awk script and machine-type input table. SH board/platform code consumes the generated `MACH_*` and `mach_is_*()` macros.

## Risks
Build reproducibility depends on stable input ordering and awk behavior. Missing dependency tracking would leave stale machine-type macros after `mach-types` changes.

## Test Signals
Run `make ARCH=sh archheaders` and verify `include/generated/machtypes.h` is regenerated and changes when `arch/sh/tools/mach-types` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/Makefile -->
