# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cprt.c

## Purpose
Implements FPA11 coprocessor register transfer, integer/float conversion, FPSR access, and comparison instructions.

## Important APIs, Types, And Functions
Exports `EmulateCPRT`, `PerformFLT`, and `PerformFIX`; internal `PerformComparison` handles CMF/CNF/CMFE/CNFE variants. Uses `readRegister`, `writeRegister`, `readFPSR`, `writeFPSR`, `writeConditionCodes`, SoftFloat conversion/comparison helpers, and opcode decode macros.

## Control Flow
`EmulateCPRT` fast-paths comparison opcodes, otherwise dispatches FLT, FIX, WFS, or RFS. `PerformFLT` converts an integer ARM register to requested FPA precision. `PerformFIX` converts an FPA register to a 32-bit integer ARM register. Comparisons resolve constants or registers, promote as needed, handle optional negated comparison, set N/Z/C/V flags, and raise invalid exceptions for unordered extended comparisons when required.

## State, Dependencies, And Integration
State includes FPA11 registers/type tags/FPSR and saved user ARM registers/CPSR. Dependencies are `fpa11.inl`, `fpmodule.inl`, SoftFloat, and `fpopcode.h`. Integrated via `EmulateAll` and `entry.S`.

## Risks And Test Signals
Risks are condition-code compatibility, NaN/unordered behavior, FPSR sysid preservation, conversion rounding exceptions, and unsupported FPCR operations. Test signals are FLT/FIX tests, FPSR read/write, all compare variants including NaNs, and CPSR flag validation.
