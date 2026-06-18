<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/common/Makefile

## Purpose
Build manifest for ARM common support objects.

## Important APIs/types/functions
- Always builds `firmware.o`.
- Conditional objects: `sa1111.o`, `krait-l2-accessors.o`, `locomo.o`, `sharpsl_param.o`, `scoop.o`, `secure_cntvoff.o`, `mcpm_head.o`, `mcpm_entry.o`, `mcpm_platsmp.o`, `vlock.o`, `bL_switcher.o`, and `bL_switcher_dummy_if.o`.
- `CFLAGS_REMOVE_mcpm_entry.o = -pg` prevents function graph/profile instrumentation in sensitive MCPM entry code.

## Control flow
Kbuild maps config symbols to object files and links them into the ARM kernel or modules as appropriate.

## State and persistence behavior
No runtime state. It defines which support code is present in the kernel image.

## Dependencies and integration points
Integrates with Kconfig symbols, ARM common code, MCPM, CPUv7 timer offset setup, and legacy companion-chip drivers.

## Risks and edge cases
Profiling removal for `mcpm_entry.o` is important because low-level power paths cannot tolerate instrumentation. Missing object gating can create unresolved symbols or unsupported hardware access.

## Test signals
Run ARM allyesconfig/defconfig builds and platform-specific builds for SA1111, LoCoMo, MCPM, BL switcher, and Krait targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Makefile -->
