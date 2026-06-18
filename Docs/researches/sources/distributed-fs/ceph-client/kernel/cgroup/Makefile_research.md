# sources/distributed-fs/ceph-client/kernel/cgroup/Makefile

## Purpose

`kernel/cgroup/Makefile` selects the object files that make up the kernel cgroup subsystem. It always builds the core cgroup implementation, rstat accounting, namespace support, cgroup v1 compatibility, and freezer core, then conditionally includes controller-specific implementations based on Kconfig symbols.

## Important build entries

- `obj-y := cgroup.o rstat.o namespace.o cgroup-v1.o freezer.o` makes the core cgroup subsystem built-in for this kernel tree.
- `obj-$(CONFIG_CGROUP_FREEZER) += legacy_freezer.o` adds the legacy freezer controller when enabled.
- `obj-$(CONFIG_CGROUP_PIDS) += pids.o`, `obj-$(CONFIG_CGROUP_RDMA) += rdma.o`, `obj-$(CONFIG_CGROUP_MISC) += misc.o`, and `obj-$(CONFIG_CGROUP_DMEM) += dmem.o` add optional controllers.
- `obj-$(CONFIG_CPUSETS) += cpuset.o` and `obj-$(CONFIG_CPUSETS_V1) += cpuset-v1.o` split common cpuset support from v1-specific behavior.
- `obj-$(CONFIG_CGROUP_DEBUG) += debug.o` includes debug controller/files only in debug builds.

## Control flow

This file has no runtime control flow. Kbuild evaluates the `obj-y` and `obj-$(CONFIG_...)` assignments to decide which C sources are compiled and linked into the kernel. Runtime availability of controllers, files, and mount options is shaped by these build choices.

## State and persistence behavior

There is no state in the Makefile itself. Its build-time decisions determine which runtime global state exists, such as pids controller state, rdma resource accounting state, cpuset state, debug files, and cgroup v1 support.

## Dependencies and integration points

The Makefile depends on cgroup-related Kconfig symbols and Kbuild conventions. It integrates the source files in this directory into the kernel's built-in object list. `cgroup-v1.o` is always present here, so boot-time and mount-time logic must disable v1 features through runtime configuration rather than absence of this object unless the broader tree changes the build model.

## Risks and edge cases

- Adding a new controller source requires both Kconfig and Makefile updates; missing the Makefile entry silently omits the implementation from builds.
- Always building `cgroup-v1.o` means v1 compatibility code remains compiled even if no v1 controllers are enabled.
- Build configurations with cpuset common support but without `CONFIG_CPUSETS_V1` must keep v1 references properly conditional.

## Test signals

Validation is primarily matrix build coverage. Compile representative configs with all controllers enabled, minimal cgroup controllers, cpusets with and without v1 support, and cgroup debug enabled. Link failures or missing symbols indicate incorrect object selection.
