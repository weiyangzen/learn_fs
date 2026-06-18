# sources/distributed-fs/lustre-release/lnet/lnet/Makefile

## Purpose
Build definition for the LNet kernel module object. It declares `lnet.o` as a module and lists the object files linked into it, including socket acceptor and Adler checksum support.

## Important build entries
`obj-m += lnet.o` builds LNet as a module. `lnet-objs` aggregates core API/config/NID/string/RDMA/locking/message/memory descriptor/portal/socket/move/module/loopback/router/debugfs/acceptor/peer/fault/UDSP/crypto objects. `lnet-objs-$(CONFIG_SMP) = lib-cpt.o` adds CPT support when SMP is enabled. `lnet-objs += $(lnet-objs-y)` appends conditional objects. `CFLAGS_lnet_rdma.o` injects GDS/CUDA include paths. `CONFIG_GCOV_PROFILE_LNET` enables GCOV profiling.

## Control flow and integration
There is no runtime control flow. The file controls which compilation units participate in `lnet.o`, so changes directly affect symbol availability for socklnd and other LNDs. `acceptor.o` provides exported socket connection helpers used by socklnd. `adler.o` participates in LNet crypto checksum registration.

## State and persistence
Build-only state. It influences module composition and coverage instrumentation but stores no runtime state.

## Dependencies
Depends on kernel kbuild variables, optional `CONFIG_SMP`, optional `CONFIG_GCOV_PROFILE_LNET`, and environment variables for CUDA/GDS include directories.

## Risks and test signals
Removing or renaming objects can break unresolved symbols or omit required networking/crypto behavior. Test signals are successful kernel-module build, modpost symbol resolution, SMP and non-SMP builds, GCOV-profiled builds, and RDMA builds with valid/invalid CUDA or GDS include paths.
