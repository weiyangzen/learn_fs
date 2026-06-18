<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Makefile -->
# sources/distributed-fs/ceph-client/Makefile

## Purpose
Root Linux kernel Makefile. It defines the kernel version, enforces build prerequisites, normalizes source/output directories, selects toolchains, exports global flags, dispatches configuration/build/clean/install/documentation targets, and orchestrates vmlinux, modules, headers, tools, and packaging.

## Important APIs, Types, And Functions
- Version variables: `VERSION`, `PATCHLEVEL`, `SUBLEVEL`, `EXTRAVERSION`, `KERNELVERSION`, and `KERNELRELEASE`.
- Build controls: `ARCH`, `SRCARCH`, `O=`, `KBUILD_OUTPUT`, `M=`, `MO=`, `LLVM`, `CROSS_COMPILE`, `V`, `C`, `W`, `CLIPPY`.
- Global exports include compiler/linker/tool variables, `KBUILD_*FLAGS`, include paths, Rust flags, `KERNELDOC`, install paths, and module paths.
- Major targets: `all`, `vmlinux`, `modules`, `modules_install`, `prepare`, `headers`, `headers_install`, `dtbs`, documentation targets, Rust targets, checks, clean/mrproper/distclean, packages, and help.
- Build helper includes: `scripts/Kbuild.include`, compiler/clang makefiles, arch Makefile, sanitizer/debug/plugin makefiles, and modpost/vmlinux scripts.

## Control Flow
The file begins with GNU make version and internal-target checks, then performs a first-pass recursion into the output directory when needed so the rest of the build runs from the object tree. It classifies goals into config, clean, no-config, single-target, mixed-target, and normal build paths. Config targets build scripts and descend into `scripts/kconfig`; normal targets include generated config state, arch Makefile data, toolchain checks, warning/debug/sanitizer makefiles, and then recurse through Kbuild directories.

## State And Persistence
This Makefile creates and consumes the object tree, generated output Makefile, `.gitignore` for out-of-tree builds, `.config`, `include/config/*`, `include/generated/*`, `vmlinux`, built archives, modules, DTBs, headers, Rust metadata, compile databases, package staging trees, and cleaning stamps. It also reads existing `.cmd` files to preserve command-line dependency tracking.

## Dependencies And Integration Points
It is the central integration point for GNU make, scripts under `scripts/`, architecture makefiles, Kconfig, Kbuild recursion, C/Rust toolchains, LLVM/GNU binutils, objtool, pahole/BTF, dtc, documentation makefiles, selftests, and external module builds. Many downstream Makefiles rely on exported variables from this root file.

## Risks And Edge Cases
Small ordering changes can break config synchronization, out-of-tree builds, external modules, or generated-header availability. Toolchain feature detection is sensitive to `ARCH`, `LLVM`, `CROSS_COMPILE`, and arch overrides. Mixed goals are intentionally serialized; bypassing that can include stale `.config` state. Clean targets are broad and must not be pointed at unintended output trees.

## Test Signals
Representative coverage includes in-tree and `O=` builds, `make olddefconfig`, `make prepare`, `make all`, `make modules`, single-object and single-`.ko` builds, external module `M=`, `headers_install`, docs targets, `dtbs_check`, Rust availability/format targets when enabled, and `clean`, `mrproper`, `distclean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Makefile -->
