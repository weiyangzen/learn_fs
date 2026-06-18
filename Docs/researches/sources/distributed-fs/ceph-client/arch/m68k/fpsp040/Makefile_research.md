# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/Makefile

Purpose: kbuild object list for the Motorola 68040 Floating Point Software Package (FPSP) used by m68k FPU exception emulation.

Important entries: `obj-y` includes conversion helpers (`bindec.o`, `binstr.o`, `decbin.o`), exception handlers (`gen_except.o`, `kernel_ex.o`, `x_*`), operand/result helpers (`get_op.o`, `res_func.o`, `round.o`, `sto_res.o`, `util.o`), transcendental implementations (`sacos.o`, `sasin.o`, etc.), and support/errata files (`bugfix.o`, `skeleton.o`).

Control flow and state: build-time only. It links all FPSP assembly objects into the m68k kernel image for 68040 FPU handling. Runtime state is managed in the individual assembly handlers' stack frames.

Dependencies and integration: Linux kbuild and 68040/FPSP assembly conventions. The listed objects depend on shared symbols and stack offsets from `fpsp.h`.

Risks and test signals: object omission or reordering can create unresolved labels or missing exception paths. Test by building a 68040/FPSP config and running floating-point exception/emulation test programs.
