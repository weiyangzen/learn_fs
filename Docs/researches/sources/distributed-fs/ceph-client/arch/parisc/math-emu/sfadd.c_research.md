# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfadd.c

Purpose: implements `sgl_fadd`, single-precision IEEE-style addition for the PA-RISC software FPU.

Important APIs and types: the function takes left, right, destination, and status pointers using `sgl_floating_point` word encodings. It uses `Sgl_*` and `Ext_*` macros for field access, magnitude comparison, alignment, extension bits, normalization, rounding, and exception status.

Control flow: operands are copied locally and XORed to capture sign relationship. The routine handles NaNs and infinities first, including invalid opposite-signed infinity addition. It orders finite operands by magnitude, handles zero and denormal shortcuts, aligns the smaller operand into an extension word, performs addition or subtraction based on sign, normalizes cancellation or carry, rounds using the extension, then detects overflow and inexact.

State and persistence: writes one destination word and may update the status register. It does not allocate memory or maintain cross-call state.

Dependencies and integration: called by `fpudispatch.c` for class 3 `FADD` and by multi-op decode paths that emulate multiply-add as separate multiply and add on older formats.

Risks: signed-zero behavior for zero plus zero depends on rounding mode. The denormal path returns early in exact cases, so trap handling must stay aligned with PA-RISC requirements. The normalization labels and fallthrough make small changes risky.

Test signals: cover finite same-sign addition, opposite-sign cancellation, denormal operands, both-zero sign rules, infinities, signaling NaNs, overflow, inexact rounding ties, and all rounding modes.
