# sources/distributed-fs/ceph-client/drivers/net/fjes/Makefile

## Purpose
This Makefile wires the Fujitsu Extended Socket network driver into the kernel build. It defines the `fjes` composite object and gates it behind `CONFIG_FUJITSU_ES`.

## Important APIs and Functions
There are no C APIs. The important build declarations are `obj-$(CONFIG_FUJITSU_ES) += fjes.o` and `fjes-objs := fjes_main.o fjes_hw.o fjes_ethtool.o fjes_trace.o fjes_debugfs.o`.

## Control Flow
When `CONFIG_FUJITSU_ES` is enabled, Kbuild links the listed objects into `fjes.o`. `fjes_main.o` supplies module/platform/netdev lifecycle, `fjes_hw.o` supplies register/shared-memory protocol, `fjes_ethtool.o` supplies ethtool operations, `fjes_trace.o` instantiates tracepoints, and `fjes_debugfs.o` is compiled as part of the object with its own `CONFIG_DEBUG_FS` guards.

## State, Dependencies, and Integration
The Makefile integrates with the parent kernel networking build and depends on a Kconfig symbol named `CONFIG_FUJITSU_ES`. Object ordering matters for tracepoint instantiation and symbol resolution but no persistent runtime state is defined here.

## Risks and Test Signals
Risks are missing object entries when new FJES files are added, stale object names after refactors, and tracepoint build failures if `fjes_trace.o` is omitted. Test signals are successful `CONFIG_FUJITSU_ES=y` and `m` builds, plus builds with and without `CONFIG_DEBUG_FS`.
