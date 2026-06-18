<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/futex.h

## Purpose
x86 futex atomic user-memory operations and cmpxchg helpers implemented with inline assembly and exception-table recovery. The header is 98 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/futex.h>`; `#include <linux/uaccess.h>`; `#include <asm/asm.h>`; `#include <asm/errno.h>`; `#include <asm/processor.h>`; `#include <asm/smap.h>`

Notable constants/macros: `#define _ASM_X86_FUTEX_H`; `#define unsafe_atomic_op1(insn, oval, uaddr, oparg, label) \`; `#define unsafe_atomic_op2(insn, oval, uaddr, oparg, label) \`

Notable declarations and inline helpers: `#define _ASM_X86_FUTEX_H`; `#define unsafe_atomic_op1(insn, oval, uaddr, oparg, label) \`; `int oldval = 0, ret; \`; `#define unsafe_atomic_op2(insn, oval, uaddr, oparg, label) \`; `int oldval = 0, ret, tem; \`; `static __always_inline int arch_futex_atomic_op_inuser(int op, int oparg, int *oval,`; `u32 __user *uaddr)`; `static inline int futex_atomic_cmpxchg_inatomic(u32 *uval, u32 __user *uaddr,`; `u32 oldval, u32 newval)`; `int ret = 0;`

## Control Flow
arch_futex_atomic_op_inuser() scopes user access, runs xchg/xadd/CAS loops for FUTEX_OP_* and jumps to -EFAULT fixups on user faults; cmpxchg helpers compare and exchange u32 futex words.

## State and Persistence
State is user-space futex words modified atomically; kernel local old-value outputs report prior state and errors.

## Dependencies and Integration Points
Depends on futex core, uaccess scopes, SMAP handling, LOCK_PREFIX, processor alternatives, and extable EX_TYPE_EFAULT_REG encoding.

## Risks
Risks include missing user access protection, wrong condition handling, ABA-style user races expected by futex semantics, and assembly constraint/extable mistakes.

## Test Signals
Tests should include futex atomic ops on valid and faulting addresses, concurrent wait/wake stress, SMAP-enabled builds, 32/64-bit builds, and all FUTEX_OP condition codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/futex.h -->
