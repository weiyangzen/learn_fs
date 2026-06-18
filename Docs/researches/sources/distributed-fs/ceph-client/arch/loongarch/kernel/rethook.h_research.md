## sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.h

### Purpose
`rethook.h` declares the LoongArch-local rethook callback and preparation helpers shared between C and assembly rethook code.

### Important APIs, Types, And Functions
It declares `arch_rethook_trampoline_callback(struct pt_regs *regs)` and `arch_rethook_prepare(struct rethook_node *rhn, struct pt_regs *regs, bool mcount)`. The include guard is `__LOONGARCH_RETHOOK_H`.

### Control Flow
The header has no executable control flow. It allows `rethook_trampoline.S` and `rethook.c` to agree on the callback interface.

### State, Persistence, And Dependencies
No state is stored. It depends on visible declarations of `struct pt_regs` and `struct rethook_node` at inclusion sites.

### Integration Points
Included by `rethook.c`; the assembly file calls the callback by symbol rather than through this header.

### Risks
Prototype drift between this header and the assembly call ABI would break return hooks. The `bool mcount` parameter in the prepare prototype must stay consistent with generic rethook expectations.

### Test Signals
Compilation with rethook/kretprobe enabled is the main validation. Runtime tests are covered by `rethook.c` and `rethook_trampoline.S`.
