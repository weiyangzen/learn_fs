<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/Makefile -->
# sources/distributed-fs/ceph-client/kernel/futex/Makefile

Purpose: declares the futex subsystem objects built into the kernel directory. It groups the futex implementation into core state, syscall dispatch, priority-inheritance handling, requeue handling, and wait/wake handling.

Important APIs/types/functions: the Makefile sets `CONTEXT_ANALYSIS := y`, enabling sparse/context annotations to check lock acquisition and release contracts in the futex code. `obj-y` includes `core.o`, `syscalls.o`, `pi.o`, `requeue.o`, and `waitwake.o`.

Control flow: there is no runtime flow in the Makefile. At build time, kbuild compiles all five objects unconditionally as part of the futex subsystem. Feature-specific code paths inside those objects are then controlled by C preprocessor symbols such as `CONFIG_FUTEX_PI`, `CONFIG_FUTEX_PRIVATE_HASH`, `CONFIG_FUTEX_MPOL`, `CONFIG_COMPAT`, and `CONFIG_FAIL_FUTEX`.

State and persistence behavior: no runtime state is stored here. Its state effect is build composition: omitting any object would remove syscall entry points, hash-key/cleanup state, PI paths, requeue paths, or basic wait/wake functionality.

Dependencies and integration points: depends on the surrounding `kernel/Makefile` selecting the futex directory and on each object sharing declarations from `futex.h`. The context-analysis setting is important because these files use annotated lock classes and nontrivial lock handoff patterns.

Risks: build-list drift is the primary risk. Adding a futex feature without listing its object would silently fail to link; removing context analysis would reduce static checking on a concurrency-sensitive subsystem. Reordering objects is usually unimportant, but missing shared symbols between `core`, `waitwake`, `pi`, `requeue`, and `syscalls` would surface as link failures.

Test signals: allmodconfig/defconfig builds with futex options, sparse/context-analysis runs, link tests for syscall symbols, and futex selftests that exercise wait/wake, PI, requeue, robust lists, and futex2 syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/Makefile -->
