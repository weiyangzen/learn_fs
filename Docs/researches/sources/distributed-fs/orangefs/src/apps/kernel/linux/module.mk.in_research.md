# sources/distributed-fs/orangefs/src/apps/kernel/linux/module.mk.in

## Purpose
This makefile fragment defines Linux kernel-client support application sources for OrangeFS, including the userspace client process, optional threaded client core handling, and the Linux 2.4-specific `mount.pvfs2` helper.

## Important APIs, Types, and Functions
Key variables are `DIR := src/apps/kernel/linux`, `PVFS2_SEGV_BACKTRACE = @PVFS2_SEGV_BACKTRACE@`, `KERNAPPSRC`, `KERNAPPTHRSRC`, `MODCFLAGS_$(DIR)/pvfs2-client-core.c`, and `MODLDFLAGS_$(DIR)/pvfs2-client-core.o`. The fragment always includes `pvfs2-client.c`, places `pvfs2-client-core.c` in threaded or non-threaded source lists depending on `@THREADED_KMOD_HELPER@`, conditionally includes `mount.pvfs2.c` for Linux 2.4 kernel source builds, and adds kernel include paths/backtrace defines.

## Control Flow
Build-time conditionals decide source membership. `ifeq (,@THREADED_KMOD_HELPER@)` selects non-threaded versus threaded client-core variables. `ifneq (,$(LINUX24_KERNEL_SRC))` adds the mount helper only when Linux 2.4 kernel source is configured. `ifdef PVFS2_SEGV_BACKTRACE` adds a compile define for client-core.

## State and Persistence
This file affects generated binaries and object link flags only. It has no runtime state.

## Dependencies and Integration Points
It integrates with configure substitutions, top-level OrangeFS make rules, kernel interface headers under `src/kernel/linux-2.6`, and pthread linkage for `pvfs2-client-core.o`. It is part of the kernel-module client support build.

## Risks and Edge Cases
The `ifeq (,@THREADED_KMOD_HELPER@)` form is subtle and depends on configure substitution exactly. The Linux 2.4 conditional reflects legacy support; modern builds may never compile `mount.pvfs2.c`, hiding bitrot. The object-specific pthread link flag applies even when broader threading is disabled, which is intentional but easy to disturb.

## Test Signals
Build matrix coverage should include threaded and non-threaded helper settings, segv-backtrace enabled/disabled, and Linux 2.4 mount-helper inclusion if still supported. Verify `pvfs2-client-core.c` receives the kernel include path and optional backtrace define.
