<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_breakpoint.h

## Purpose
x86 hardware breakpoint interface for debug-register slot counts, masks, validation, and perf breakpoint integration. The header is 77 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <uapi/asm/hw_breakpoint.h>`; `#include <linux/kdebug.h>`; `#include <linux/percpu.h>`; `#include <linux/list.h>`

Notable constants/macros: `#define _I386_HW_BREAKPOINT_H`; `#define __ARCH_HW_BREAKPOINT_H`; `#define X86_BREAKPOINT_LEN_X 0x40`; `#define X86_BREAKPOINT_LEN_1 0x40`; `#define X86_BREAKPOINT_LEN_2 0x44`; `#define X86_BREAKPOINT_LEN_4 0x4c`; `#define X86_BREAKPOINT_LEN_8 0x48`; `#define X86_BREAKPOINT_EXECUTE 0x80`; `#define X86_BREAKPOINT_WRITE 0x81`; `#define X86_BREAKPOINT_RW 0x83`; `#define HBP_NUM 4`; `#define hw_breakpoint_slots(type) (HBP_NUM)`

Notable declarations and inline helpers: `#define _I386_HW_BREAKPOINT_H`; `#define __ARCH_HW_BREAKPOINT_H`; `struct arch_hw_breakpoint {`; `unsigned long address;`; `unsigned long mask;`; `u8 len;`; `u8 type;`; `#define X86_BREAKPOINT_LEN_X 0x40`; `#define X86_BREAKPOINT_LEN_1 0x40`; `#define X86_BREAKPOINT_LEN_2 0x44`; `#define X86_BREAKPOINT_LEN_4 0x4c`; `#define X86_BREAKPOINT_LEN_8 0x48`; `#define X86_BREAKPOINT_EXECUTE 0x80`; `#define X86_BREAKPOINT_WRITE 0x81`; `#define X86_BREAKPOINT_RW 0x83`; `#define HBP_NUM 4`; `#define hw_breakpoint_slots(type) (HBP_NUM)`; `struct perf_event_attr;`; `struct perf_event;`; `struct pmu;`; `extern int arch_check_bp_in_kernelspace(struct arch_hw_breakpoint *hw);`; `extern int hw_breakpoint_arch_parse(struct perf_event *bp,`; `struct arch_hw_breakpoint *hw);`; `extern int hw_breakpoint_exceptions_notify(struct notifier_block *unused,`

## Control Flow
Breakpoint setup validates lengths/types, encodes DR7 control bits, and coordinates debug register access through implementation functions declared here.

## State and Persistence
State lives in CPU debug registers DR0-DR7, per-task/perf breakpoint metadata, and ptrace-visible debug state.

## Dependencies and Integration Points
Depends on perf_event, ptrace, debug exception handling, processor debug registers, and notifier paths.

## Risks
Risks include leaking debug registers across tasks, wrong length/type encoding, recursion in #DB handling, and conflicts with kgdb/kprobes.

## Test Signals
Tests should cover perf breakpoints, ptrace watchpoints, task switch isolation, invalid ranges, single-step interactions, and virtualization/debug exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_breakpoint.h -->
