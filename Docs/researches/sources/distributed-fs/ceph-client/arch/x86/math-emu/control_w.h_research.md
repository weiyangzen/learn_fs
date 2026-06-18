# sources/distributed-fs/ceph-client/arch/x86/math-emu/control_w.h

## Purpose
This header defines x87 control-word bit masks used by both C and assembly emulator code, including exception masks, rounding control, and precision control.

## Important APIs, Types, and Functions
Key macros are `CW_RC`, `CW_PC`, `CW_Precision`, `CW_Underflow`, `CW_Overflow`, `CW_ZeroDiv`, `CW_Denormal`, `CW_Invalid`, `CW_Exceptions`, rounding modes `RC_RND`, `RC_DOWN`, `RC_UP`, `RC_CHOP`, precision modes `PR_24_BITS`, `PR_53_BITS`, `PR_64_BITS`, `PR_RESERVED_BITS`, and `FULL_PRECISION`. `_Const_()` adapts constants for assembler or C.

## Control Flow
There is no control flow. These constants drive branches and masking in arithmetic, load/store, and exception code.

## State and Persistence
The header defines how the persistent per-task `control_word` field is interpreted. It does not store state itself.

## Dependencies and Integration Points
It is included by emulator C and assembly files that need IEEE/x87 exception masks, rounding mode selection, and precision mode selection. It integrates closely with `exception.h`, `status_w.h`, and `fpu_system.h`.

## Risks and Test Signals
Risks include bit mismatches with hardware x87 semantics or assembler constant syntax. Test signals include correct behavior under all rounding modes, masked/unmasked exceptions, and save/restore of the control word through `fldcw`, `fstcw`, `fninit`, and regset APIs.
