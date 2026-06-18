<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kprobes.h

## Purpose
x86 kprobes architecture data for instruction slots, optimized probes, previous-probe tracking, and trap handlers. The header is 123 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm-generic/kprobes.h>`; `#include <linux/types.h>`; `#include <linux/ptrace.h>`; `#include <linux/percpu.h>`; `#include <asm/text-patching.h>`; `#include <asm/insn.h>`

Notable constants/macros: `#define _ASM_X86_KPROBES_H`; `#define __ARCH_WANT_KPROBES_INSN_SLOT`; `#define MAX_STACK_SIZE 64`; `#define CUR_STACK_SIZE(ADDR) \`; `#define MIN_STACK_SIZE(ADDR) \`; `#define flush_insn_slot(p) do { } while (0)`; `#define MAX_OPTIMIZED_LENGTH (MAX_INSN_SIZE + DISP32_SIZE)`; `#define MAX_OPTINSN_SIZE \`

Notable declarations and inline helpers: `#define _ASM_X86_KPROBES_H`; `#define __ARCH_WANT_KPROBES_INSN_SLOT`; `struct pt_regs;`; `struct kprobe;`; `typedef u8 kprobe_opcode_t;`; `#define MAX_STACK_SIZE 64`; `#define CUR_STACK_SIZE(ADDR) \`; `#define MIN_STACK_SIZE(ADDR) \`; `#define flush_insn_slot(p) do { } while (0)`; `extern __visible kprobe_opcode_t optprobe_template_entry[];`; `extern __visible kprobe_opcode_t optprobe_template_clac[];`; `extern __visible kprobe_opcode_t optprobe_template_val[];`; `extern __visible kprobe_opcode_t optprobe_template_call[];`; `extern __visible kprobe_opcode_t optprobe_template_end[];`; `#define MAX_OPTIMIZED_LENGTH (MAX_INSN_SIZE + DISP32_SIZE)`; `#define MAX_OPTINSN_SIZE \`; `extern const int kretprobe_blacklist_size;`; `void arch_remove_kprobe(struct kprobe *p);`; `struct arch_specific_insn {`; `unsigned boostable:1;`; `unsigned char size; /* The size of insn */`; `union {`; `unsigned char opcode;`; `struct {`

## Control Flow
Kprobe preparation decodes copied instructions, records fixups/relocations, patches int3 or optimized detour templates, and trap handlers dispatch pre/post/fault processing.

## State and Persistence
State is per-probe arch_specific_insn, optimized instruction buffers, per-CPU kprobe_ctlblk/current probe tracking, and patched text slots.

## Dependencies and Integration Points
Depends on generic kprobes, text patching, insn decoder, pt_regs, optprobe templates, int3/debug exception handling, and retprobe blacklist.

## Risks
Risks include probing unsafe instructions, bad RIP-relative relocation, stack-size checks, text patch races, and conflicts with ftrace/kgdb/livepatch.

## Test Signals
Tests should run kprobe selftests, optimized/unoptimized probes, kretprobes, RIP-relative instructions, fault injection, blacklist coverage, and module probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kprobes.h -->
