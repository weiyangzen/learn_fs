<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_count.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_count.h

## Purpose
This header computes the maximum number of enabled Linux Security Modules at compile time. The result sizes static-call tables and other LSM stacking arrays.

## Important APIs, Types, and Functions
It defines per-LSM enabled-list macros for capabilities, SELinux, Smack, AppArmor, TOMOYO, Yama, LoadPin, Lockdown, SafeSetID, BPF LSM, Landlock, IMA, EVM, and IPE. `COUNT_LSMS()` uses variadic argument counting from `linux/args.h`, and `MAX_LSM_COUNT` expands to the computed count when security is enabled, otherwise zero.

## Control Flow
There is no runtime flow. Preprocessor conditionals include one marker per configured LSM, and macro argument counting produces a compile-time integer.

## State and Persistence Behavior
No state exists. The count affects compiled object sizes and static-call table layout.

## Dependencies and Integration Points
It depends on Kconfig symbols and `linux/args.h`. It integrates with `lsm_hooks.h` static-call table definitions.

## Risks and Test Signals
Risks include forgetting to add a new LSM, over- or under-sizing static-call arrays, and disabled-security build regressions. Test signals are all LSM Kconfig matrix builds, static assertions around table sizes, and boot logs showing expected enabled LSMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_count.h -->
