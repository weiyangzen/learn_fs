<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufeature.h -->
# sources/distributed-fs/ceph-client/include/linux/cpufeature.h

## Purpose

`cpufeature.h` provides a generic module autoprobed-by-CPU-feature helper when architectures enable `CONFIG_GENERIC_CPU_AUTOPROBE`. The source was read as a complete 58-line file.

## Important APIs, Types, and Functions

The central API is `module_cpu_feature_match(feature, initfunc)`. It emits a `struct cpu_feature` match table, exports it via `MODULE_DEVICE_TABLE(cpu, ...)`, and wraps module initialization so the module returns `-ENODEV` if `cpu_have_feature(cpu_feature(feature))` is false. It relies on architecture-provided `cpu_feature()`, `cpu_have_feature()`, `MAX_CPU_FEATURES`, and optional `CPU_FEATURE_TYPEFMT`/`CPU_FEATURE_TYPEVAL`.

## Control Flow

For supported architectures, module loading or udev autoloading matches CPU feature modalias data. During module init, the wrapper checks the feature again before calling the real init function, preventing manual load on unsupported CPUs.

## State and Persistence Behavior

The header creates static const match tables in modules. It owns no runtime mutable state.

## Dependencies and Integration Points

It includes `linux/init.h`, `linux/mod_devicetable.h`, and `asm/cpufeature.h` only under `CONFIG_GENERIC_CPU_AUTOPROBE`. It integrates with module autoloading, architecture CPU feature enumeration, and feature-specific drivers or accelerators.

## Risks and Edge Cases

The macro depends on legal architecture feature names. Generated symbol names include the feature token, so unusual macro arguments can break compilation. Runtime feature checks must match modalias feature enumeration or autoload and manual-load behavior diverge.

## Test Signals

Signals include module build tests on architectures with and without generic autoprobe, modalias generation checks, manual insmod on unsupported feature returning `-ENODEV`, and successful init on CPUs with the feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufeature.h -->
