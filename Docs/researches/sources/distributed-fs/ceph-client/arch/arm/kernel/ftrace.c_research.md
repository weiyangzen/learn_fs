# sources/distributed-fs/ceph-client/arch/arm/kernel/ftrace.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/ftrace.c` patches ARM ftrace call sites and
handles function graph return rewriting. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 323 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arch_ftrace_update_code(), ftrace_make_call(),
ftrace_modify_call(), ftrace_make_nop(), ftrace_update_ftrace_func(), prepare_ftrace_return(), and
graph caller enable/disable helpers.
Visible dependencies include: `linux/ftrace.h`, `linux/uaccess.h`, `linux/module.h`,
`linux/stop_machine.h`, `asm/cacheflush.h`, `asm/opcodes.h`, `asm/ftrace.h`, `asm/insn.h`,
`asm/set_memory.h`, `asm/stacktrace.h`, `asm/text-patching.h`.
Important macros/constants include: `NOP`.
C functions detected in this file include: `__ftrace_modify_code()`, `arch_ftrace_update_code()`,
`ftrace_nop_replace()`, `adjust_address()`, `ftrace_arch_code_modify_prepare()`,
`ftrace_arch_code_modify_post_process()`, `ftrace_call_replace()`, `ftrace_modify_code()`,
`ftrace_update_ftrace_func()`, `ftrace_make_call()`, `ftrace_modify_call()`, `ftrace_make_nop()`,
`prepare_ftrace_return()`, `__ftrace_modify_caller()`, `ftrace_modify_graph_caller()`,
`ftrace_enable_ftrace_graph_caller()`, `ftrace_disable_ftrace_graph_caller()`.

## Control Flow
stop_machine-driven text patching replaces mcount sequences with NOP or branch-link instructions and
graph tracing swaps return addresses.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: instruction encoding, module PLT reachability, init-text veneers, and cache/TLB
synchronization are critical. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
