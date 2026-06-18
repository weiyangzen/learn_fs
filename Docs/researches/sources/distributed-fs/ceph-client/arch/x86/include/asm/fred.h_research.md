<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fred.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fred.h

## Purpose
Flexible Return and Event Delivery definitions for FRED opcodes, stack-frame layout, entrypoints, RSP0 synchronization, and KVM event injection. The header is 119 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/const.h>`; `#include <asm/asm.h>`; `#include <asm/msr.h>`; `#include <asm/trapnr.h>`; `#include <linux/kernel.h>`; `#include <linux/sched/task_stack.h>`; `#include <asm/ptrace.h>`

Notable constants/macros: `#define ASM_X86_FRED_H`; `#define ERETS _ASM_BYTES(0xf2,0x0f,0x01,0xca)`; `#define ERETU _ASM_BYTES(0xf3,0x0f,0x01,0xca)`; `#define FRED_STACK_FRAME_RSP_MASK _AT(unsigned long, (~0x3f))`; `#define FRED_CONFIG_REDZONE_AMOUNT 1`; `#define FRED_CONFIG_REDZONE (_AT(unsigned long, FRED_CONFIG_REDZONE_AMOUNT) << 6)`; `#define FRED_CONFIG_INT_STKLVL(l) (_AT(unsigned long, l) << 9)`; `#define FRED_CONFIG_ENTRYPOINT(p) _AT(unsigned long, (p))`

Notable declarations and inline helpers: `#define ASM_X86_FRED_H`; `#define ERETS _ASM_BYTES(0xf2,0x0f,0x01,0xca)`; `#define ERETU _ASM_BYTES(0xf3,0x0f,0x01,0xca)`; `#define FRED_STACK_FRAME_RSP_MASK _AT(unsigned long, (~0x3f))`; `#define FRED_CONFIG_REDZONE_AMOUNT 1`; `#define FRED_CONFIG_REDZONE (_AT(unsigned long, FRED_CONFIG_REDZONE_AMOUNT) << 6)`; `#define FRED_CONFIG_INT_STKLVL(l) (_AT(unsigned long, l) << 9)`; `#define FRED_CONFIG_ENTRYPOINT(p) _AT(unsigned long, (p))`; `struct fred_info {`; `unsigned long edata;`; `unsigned long resv;`; `struct fred_frame {`; `struct pt_regs regs;`; `struct fred_info info;`; `static __always_inline struct fred_info *fred_info(struct pt_regs *regs)`; `static __always_inline unsigned long fred_event_data(struct pt_regs *regs)`; `void asm_fred_entrypoint_user(void);`; `void asm_fred_entrypoint_kernel(void);`; `void asm_fred_entry_from_kvm(struct fred_ss);`; `static __always_inline void fred_entry_from_kvm(unsigned int type, unsigned int vector)`; `struct fred_ss ss = {`; `void cpu_init_fred_exceptions(void);`; `void cpu_init_fred_rsps(void);`; `void fred_complete_exception_setup(void);`

## Control Flow
FRED entry code builds a fred_frame containing pt_regs plus event data; fred_update_rsp0 writes MSR_IA32_FRED_RSP0 only when current task stack top changes.

## State and Persistence
State is per-CPU fred_rsp0 and hardware FRED MSRs; event data is transient in the FRED stack frame.

## Dependencies and Integration Points
Depends on MSR accessors, trap numbers, pt_regs, task stack layout, CPU feature checks, and KVM FRED injection helpers.

## Risks
Risks include stale RSP0 after task switch, wrong event type/vector encoding, binutils opcode compatibility, and divergence from IDT paths.

## Test Signals
Tests should cover boot with FRED enabled/disabled, exception/interrupt delivery, NMI/KVM injected events, task switch RSP0 updates, and fallback stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fred.h -->
