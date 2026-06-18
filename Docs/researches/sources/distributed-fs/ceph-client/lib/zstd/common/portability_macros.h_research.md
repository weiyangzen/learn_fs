# sources/distributed-fs/ceph-client/lib/zstd/common/portability_macros.h

## Purpose
`portability_macros.h` is a macro-only portability shim shared by C and assembly. In this kernel tree it mainly normalizes compiler feature probes, defines symbol-hiding annotations for assembly, controls dynamic BMI2 detection, and disables the x86-64 BMI2 assembly enable macro.

## Important Macros
Fallback definitions for `__has_attribute`, `__has_builtin`, and `__has_feature` support non-Clang compilers. `ZSTD_HIDE_ASM_FUNCTION(func)` maps to `.hidden`, `.private_extern`, or nothing depending on object format. `DYNAMIC_BMI2` becomes enabled for supported GCC/Clang x86 builds when BMI2 is not already a compile-time target. `ZSTD_ASM_SUPPORTED` is set to `1`, but `ZSTD_ENABLE_ASM_X86_64_BMI2` is set to `0` in this copy. CET support is optionally wired through `<cet.h>` and `ZSTD_CET_ENDBRANCH`.

## Control Flow and State
There is no runtime state and no C code by design. The only behavior is preprocessor selection. Downstream source files compile BMI2-targeted functions under `DYNAMIC_BMI2` and assembly code under `ZSTD_ENABLE_ASM_X86_64_BMI2`; this file's values therefore choose which implementation variants exist in the build.

## Dependencies and Integration Points
The header may include `<cet.h>` if available and `__has_include` reports it. It is consumed by compiler/cpu/assembly-adjacent code in Zstd, including HUF/FSE BMI2 dispatch paths. Kernel configuration and compiler flags can override macros before inclusion.

## Risks and Test Signals
Risk comes from configuration drift: `ZSTD_ASM_SUPPORTED` says assembly is generally supported while `ZSTD_ENABLE_ASM_X86_64_BMI2` forces the specific BMI2 assembly path off. If future code assumes these are correlated, build or dispatch bugs can appear. Tests should include x86 builds with and without `__BMI2__`, non-x86 builds, CET-enabled builds, and preprocessed checks confirming no assembly-only C constructs leak into this macro-only header.
