# sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess-asm.h

## Purpose
Defines assembly macros and constants for ARM user-access routines, including fault-table labels and address-limit checks.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_UACCESS_ASM_H__, DACR(x...), DACR(x...), PAN(x...), PAN(x...). Assembly macros include .macro csdb, .macro check_uaccess, addr:req, size:req, limit:req, tmp:req, bad:req, .macro uaccess_mask_range_ptr, addr:req, size:req, limit:req, tmp:req, .macro uaccess_disable, tmp, isb=1, .macro uaccess_enable, tmp, isb=1, .macro uaccess_disable, tmp, isb=1, .macro uaccess_enable, tmp, isb=1, .macro uaccess_disable, tmp, isb=1. It depends directly on #include <asm/asm-offsets.h>, #include <asm/domain.h>, #include <asm/page.h>, #include <asm/thread_info.h>.

## Control Flow
Low-level copy/get/put user assembly includes these macros to validate user addresses and branch to exception fixups.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/asm-offsets.h>, #include <asm/domain.h>, #include <asm/page.h>, #include <asm/thread_info.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Signals include uaccess fault-injection tests, copy_to/from_user and get_user/put_user behavior across valid and invalid pointers, seccomp/ptrace syscall tests, and Spectre/PAN configuration boot tests.
