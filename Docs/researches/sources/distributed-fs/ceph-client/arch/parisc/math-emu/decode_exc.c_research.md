# sources/distributed-fs/ceph-client/arch/parisc/math-emu/decode_exc.c

Purpose: decodes queued PA-RISC FPU exception registers, completes unimplemented instructions through `fpudispatch()`, and returns Linux signal/code encodings when a real trap remains.

Important APIs/types/functions: `decode_fpu(unsigned int Fpu_register[], unsigned int trap_counts[])` is the external interface. Local macros map `Fpu_register[0]` to the FPU status word, extract exception type/instruction fields, address single/double/quad registers, and construct `SIGNALCODE(signal, code)`.

Control flow: it saves accrued status flags, clears the architectural flag field for processing, rejects reserved operations when the T-bit is clear, then scans exception registers 1 through 7. Unimplemented exceptions are cleared and emulated through `fpudispatch`; new emulation exceptions are written back into the queue. Underflow and overflow are either reported as traps or converted to default results and flags when traps are disabled. Invalid, divide-by-zero, and inexact become `SIGFPE` codes; unknown exceptions become `SIGILL`.

State and dependencies: mutates the passed FPU register image, exception registers, T-bit, status flags, and target result registers. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, `cnv_float.h`, `denormal.c`, `fpudispatch`, Linux signal constants, and `printk`.

Risks: exception queue mutation order is delicate. Trap-disabled underflow/overflow must match hardware default-result rules. `trap_counts` is effectively unused despite being passed. Status flag preservation is a compatibility-sensitive area.

Test signals: FPU exception tests for each enabled/disabled trap, queued multiple exceptions, unimplemented instruction emulation, denormalized default results, signal delivery codes, and status-word bit preservation.
