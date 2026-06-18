# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fmpyfadd.c

Purpose: implements PA-RISC fused multiply-add emulation for double and single precision: `dbl_fmpyfadd`, `dbl_fmpynfadd`, `sgl_fmpyfadd`, and `sgl_fmpynfadd`. The non-negated forms compute `(src1 * src2) + src3`; the negated forms flip the product sign before adding.

Important APIs and types: the entry points take `dbl_floating_point` or `sgl_floating_point` pointers plus an FP status word pointer. They rely heavily on `float.h`, `sgl_float.h`, and `dbl_float.h` macros for IEEE fields, hidden bits, extended intermediates, trap tests, rounding mode, and exception flag updates.

Control flow: each routine copies operands into integer words, precomputes the product sign and exponent, handles NaNs, infinities, zero products, and denormals, multiplies significands into an extended exact accumulator, aligns the addend, chooses add versus subtract by sign, normalizes cancellation or overflow, rounds once, then writes the destination and exception status. The double path uses four-word `Dblext` temporaries; the single path uses two-word `Sglext` temporaries.

State and persistence: no persistent state is stored locally, but the routines mutate the pointed status register through macros such as `Set_invalidflag`, `Set_overflowflag`, `Set_underflowflag`, and `Set_inexactflag`. Destination memory is written only after a result or trap-wrapped result is known.

Dependencies and integration: `fpudispatch.c` calls these functions from major opcode `0x2e` decode. Correctness depends on bit-level helper macros, PA-RISC exception codes such as `OPC_2E_INVALIDEXCEPTION`, and the register image layout used by the FPU trap handler.

Risks: the file contains four large near-duplicate K&R-style bodies, making fixes easy to miss in one precision or sign variant. Rounding fallthrough from `ROUNDMINUS` to `ROUNDZERO` is intentional but fragile. Corner cases include signed zero selection, invalid infinity subtraction, denormal underflow traps, and exact cancellation.

Test signals: exercise NaN precedence, signaling NaNs with traps enabled and disabled, `inf * 0`, product infinity plus opposite infinity, addend zero, denormal operands, all rounding modes, overflow and underflow trap wrapping, inexact traps, and cancellation to signed zero.
