# sources/distributed-fs/ceph-client/drivers/idle/Makefile

## Purpose

`drivers/idle/Makefile` builds idle-driver objects for this directory, currently the Intel cpuidle driver, and applies a compile flag when branch profiling is enabled.

## Important APIs, Types, and Functions

- `ccflags-$(CONFIG_TRACE_BRANCH_PROFILING) += -DDISABLE_BRANCH_PROFILING` disables branch profiling instrumentation for this directory when branch profiling is configured.
- `obj-$(CONFIG_INTEL_IDLE) += intel_idle.o` includes the Intel idle driver object when `INTEL_IDLE` is enabled.

## Control Flow

The kernel build system expands conditional variables from active Kconfig symbols. If trace branch profiling is enabled, compilation receives `-DDISABLE_BRANCH_PROFILING`; if Intel idle is enabled, `intel_idle.o` is added to built objects.

## State and Persistence Behavior

The Makefile has build-time effects only and stores no runtime state.

## Dependencies and Integration Points

It depends on Kbuild conditional variable semantics and the `INTEL_IDLE`/`TRACE_BRANCH_PROFILING` symbols. It integrates with `drivers/idle/Kconfig` and the `intel_idle.c` source in the same directory.

## Risks and Edge Cases

The branch profiling flag is safety-related because the comment notes branch profiling is not `noinstr` safe. Removing or scoping it incorrectly could instrument code that must remain noinstr-safe. Missing `obj-$(CONFIG_INTEL_IDLE)` would silently drop the driver from builds.

## Test Signals

Build with `CONFIG_INTEL_IDLE=y` and verify `intel_idle.o` is compiled. Build with `CONFIG_TRACE_BRANCH_PROFILING=y` and inspect compile commands for `-DDISABLE_BRANCH_PROFILING`.
