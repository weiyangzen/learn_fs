# sources/distributed-fs/ceph-client/arch/m68k/68000/ints.h

Purpose: tiny local declaration header connecting 68000 assembly interrupt entry code with the C interrupt dispatcher.

The only API is `asmlinkage void process_int(int vec, struct pt_regs *fp);`, with a forward declaration for `struct pt_regs`. The `asmlinkage` marker preserves the calling convention expected by `entry.S`, where vector and frame pointer are pushed on the stack before `jbsr process_int`.

State and persistence: none. The header does not define data, macros, or inline functions.

Dependencies are `linux/linkage.h` for `asmlinkage` and the architecture `pt_regs` type supplied elsewhere. Integration is local to `68000/ints.c` and `68000/entry.S`.

Risks and test signals: changing the prototype or dropping `asmlinkage` would silently break the assembly/C ABI. Compile coverage of `entry.S` and `ints.c` together is the primary test; runtime evidence is successful interrupt dispatch into `process_int()` with a valid register frame.
