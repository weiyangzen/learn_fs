# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-ftrace.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-ftrace.S` implements ARM ftrace and
function graph assembly trampolines. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 302 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __gnu_mcount_nc, ftrace_caller, ftrace_regs_caller,
ftrace_graph_caller, return_to_handler, ftrace_stub, and init trampolines.
Visible dependencies include: `asm/assembler.h`, `asm/ftrace.h`, `asm/unwind.h`, `entry-header.S`.
Assembly entry points detected in this file include: `__gnu_mcount_nc`, `ftrace_caller`,
`ftrace_regs_caller`, `ftrace_graph_caller`, `ftrace_graph_regs_caller`, `return_to_handler`,
`ftrace_stub`, `ftrace_stub_graph`, `\dst\(`.

## Control Flow
mcount call sites save registers, call dynamic ftrace hooks, optionally enter graph tracing, and
restore execution.

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
Primary risk: register save layout must match ftrace.c and unwinder expectations or tracing corrupts
kernel execution. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
