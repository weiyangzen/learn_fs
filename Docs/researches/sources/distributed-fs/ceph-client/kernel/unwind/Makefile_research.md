<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/Makefile -->
# sources/distributed-fs/ceph-client/kernel/unwind/Makefile

Purpose: builds the generic user-space unwind implementation when `CONFIG_UNWIND_USER` is enabled.

Important rule: `obj-$(CONFIG_UNWIND_USER) += user.o deferred.o` compiles both direct frame-pointer unwinding and deferred task-work unwinding as one feature.

Control flow and integration: the Makefile is the bridge from Kconfig to `kernel/unwind/user.o` and `kernel/unwind/deferred.o`. If the option is disabled, none of the generic user unwind code from this directory is linked.

State and persistence: no runtime state is defined here.

Dependencies and risks: build correctness depends on headers and architecture hooks required by both objects being available whenever `CONFIG_UNWIND_USER=y` or `m` is selected. Test signals are configuration build tests with the option enabled and disabled, including architectures with and without frame-pointer user unwind support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/Makefile -->
