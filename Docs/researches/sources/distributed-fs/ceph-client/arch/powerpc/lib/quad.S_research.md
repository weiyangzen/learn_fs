# sources/distributed-fs/ceph-client/arch/powerpc/lib/quad.S

`quad.S` provides quadword load/store helpers for instruction emulation. It exports `do_lq`, `do_stq`, `do_lqarx`, and `do_stqcx`. These wrap PowerPC quadword and atomic quadword instructions and convert memory faults into `-EFAULT`.

`do_lq(ea, regs)` executes `lq` from effective address `ea`, stores the two result GPR values into `regs[0]` and `regs[1]`, and returns zero. `do_stq(ea, val0, val1)` stores the register pair with `stq`. `do_lqarx(ea, regs)` performs a reservation-form quadword load using `PPC_LQARX`, and `do_stqcx(ea, val0, val1, crp)` performs conditional quadword store, writes the resulting condition register to `*crp`, and returns zero. Each instruction has an `EX_TABLE` entry that branches to a `-EFAULT` return path.

State includes reservation state for lqarx/stqcx and the caller-provided output buffers. Dependencies include PPC opcode macros, exception tables, instruction emulation, and ABI pairing of registers. Risks are clobbering the wrong CR value, reservation semantics differing from emulated instruction expectations, and fault recovery after partial state changes. Test signals include emulate-step tests for lq/stq/lqarx/stqcx, alignment/fault injection, and transactional/atomic instruction emulation coverage.
