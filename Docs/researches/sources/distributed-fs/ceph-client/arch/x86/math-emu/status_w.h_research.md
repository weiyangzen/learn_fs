# sources/distributed-fs/ceph-client/arch/x86/math-emu/status_w.h

## Purpose
Defines x87 status-word bit masks and small helpers for manipulating emulator status flags.

## Important APIs, Types, And Functions
Macros define exception bits (`SW_Invalid`, `SW_Denorm_Op`, `SW_Zero_Div`, `SW_Overflow`, `SW_Underflow`, `SW_Precision`), stack fault, summary/backward flags, condition codes, top-of-stack shift, and busy bit. Helpers include `clear_C1()`, `set_C1()`, `setcc(cc)`, `status_word()`, and `status_word_and_BUSY()`.

## Control Flow
Header-only macros update `partial_status` and combine it with `top` to synthesize the architectural status word.

## State And Persistence
All helpers operate on global emulator state such as `partial_status` and `top`; no storage is declared here.

## Dependencies And Integration Points
Included by comparison, constants, load/store, and exception/status paths. It is the shared definition of condition and exception flag layout.

## Risks
Bit definitions must match x87 architectural layout. `setcc()` preserves non-condition bits while replacing `C0/C1/C2/C3`; misuse can unintentionally clear `C1`.

## Test Signals
Instruction-level tests that inspect `fnstsw`, condition codes after compare/classification, stack-top reporting, busy bit synthesis, and exception-summary behavior.
