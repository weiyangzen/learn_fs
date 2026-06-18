# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Makefile

## Purpose
This Makefile builds the CoreSight framework and component drivers selected by CoreSight Kconfig symbols, while enabling an elevated warning set for this subdirectory.

## Important APIs, Types, And Functions
There are no runtime functions. Important build aggregates include `coresight-y`, `coresight-tmc-y`, `coresight-etm3x-y`, `coresight-etm4x-y`, `coresight-cti-y`, and `coresight-ctcu-y`. It also sets `CFLAGS_coresight-stm.o := -D__DISABLE_TRACE_MMIO__`.

## Control Flow
Kbuild adds warning flags through `subdir-ccflags-y`, conditionally adds supported compiler warning flags through `cc-option`, and maps each `CONFIG_CORESIGHT_*` symbol to either a single object or a multi-object module. The base `CONFIG_CORESIGHT` target builds the core framework pieces, including platform, sysfs, syscfg/configfs, perf, trace ID, and preloaded configurations.

## State And Persistence
The file only controls compilation and linking. It does not define runtime state, but its object grouping determines module boundaries and which init/exit paths are linked together.

## Dependencies And Integration Points
It consumes symbols from `drivers/hwtracing/coresight/Kconfig`. It integrates with the kernel build system's per-directory CFLAGS, compiler feature probing, composite object syntax, and CoreSight component source files.

## Risks
- Kconfig/Makefile drift can leave a visible config symbol with no object or an object built under the wrong symbol.
- Stricter warning flags can break builds on compiler versions not covered by `cc-option`; unconditional flags must remain broadly supported.
- Composite object membership controls module contents, so missing a source file can produce runtime registration gaps even when the module builds.
- The STM-specific `__DISABLE_TRACE_MMIO__` define changes instrumentation behavior and must stay limited to `coresight-stm.o`.

## Test Signals
Run build matrix checks for each CoreSight symbol, `W=1` style warning coverage, GCC and Clang support for conditional flags, module contents for composite targets, and KUnit build inclusion under `CONFIG_CORESIGHT_KUNIT_TESTS`.
