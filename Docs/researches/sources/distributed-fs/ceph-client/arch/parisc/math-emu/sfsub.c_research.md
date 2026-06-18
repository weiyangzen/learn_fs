# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsub.c

Purpose: implements `sgl_fsub`, single-precision subtraction for the PA-RISC software FPU.

Important APIs and types: signature mirrors `sgl_fadd`. It uses the same single-precision field and extension macros, but interprets the operand sign relation oppositely for subtract semantics.

Control flow: after copying operands and computing an XOR sign save, the routine handles NaNs and infinities. Same-signed infinities in subtraction are invalid; a right infinity returns with inverted sign. Finite operands are ordered by magnitude, with the larger operand becoming left and possibly sign-inverted. Zero and denormal shortcuts are handled exactly. The main path aligns the smaller operand, subtracts or adds magnitudes, normalizes cancellation, rounds from the extension word, then checks overflow and inexact.

State and persistence: writes destination and status flags only. No persistent memory is retained.

Dependencies and integration: called by `fpudispatch.c` for `FSUB` and by `decode_26` multi-op emulation. Shares most algorithmic structure with `sfadd.c`.

Risks: because this file is almost a sign-variant of addition, divergences from `sfadd.c` need careful review. Signed-zero selection, infinity invalid rules, and sign inversion after magnitude swapping are common bug sites.

Test signals: subtract equal finite numbers, opposite zero combinations, normal minus subnormal, subnormal minus normal, infinities with same and opposite signs, NaNs, overflow, inexact rounding, and all rounding modes.
