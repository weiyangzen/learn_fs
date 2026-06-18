<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/cpufeaturemasks.awk -->
# sources/distributed-fs/ceph-client/arch/x86/tools/cpufeaturemasks.awk

## Purpose
`cpufeaturemasks.awk` converts `cpufeatures.h` plus `.config` into C preprocessor masks for compile-time required and disabled x86 CPU features.

## Important APIs, types, and functions
It emits `REQUIRED_MASKn`, `DISABLED_MASKn`, and `*_MASK_BIT_SET(x)` macros. Internally it builds `feats[]` from `X86_FEATURE_*`, reads `NCAPINTS`, and maps `CONFIG_X86_REQUIRED_FEATURE_*`/`CONFIG_X86_DISABLED_FEATURE_*` settings.

## Control flow
The script processes two inputs with different field separators, accumulates feature status, prints comments naming selected features, and emits one 32-bit mask per capability word.

## State and persistence behavior
State is transient AWK arrays. The generated header persists in the build tree and is consumed by CPU feature policy code.

## Dependencies and integration points
It depends on the exact macro shape in `arch/x86/include/asm/cpufeatures.h` and config option naming conventions.

## Risks and edge cases
Feature-word parsing assumes every word has at least one feature and uses AWK exponentiation for bit masks; unusual AWK behavior or macro format changes can generate wrong masks.

## Test signals
Signals are generated header diffs after CPU feature changes, build coverage with required/disabled feature configs, and runtime boot checks that required feature enforcement matches config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/cpufeaturemasks.awk -->
