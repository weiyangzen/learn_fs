# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-biffuncs.h

Purpose: provides small bit-manipulation helpers used by Medusa video register programming.

Important APIs and functions: `SetBit(Bit)` expands to `1 << Bit`; `getBit(sample, index)` extracts a bit as `u8`; `clearBitAtPos(value, bit)` clears one bit in a `u32`; `setBitAtPos(sample, bit)` sets one bit in a `u32`.

Control flow: inline helpers are used in read-modify-write sequences for Medusa decoder registers, especially `MISC_TIM_CTRL`, DENC enable bits, and procamp-related control paths.

State and persistence: no state. Helpers return computed values for callers to write to hardware.

Dependencies and integration points: depends on Linux fixed-width aliases `u8` and `u32`, normally available through the including driver headers. Included directly by `cx25821-medusa-video.c`.

Risks: shifts are unguarded; bit indexes outside the width of `int`/`u32` would be undefined. `SetBit` uses `1` rather than `1U`, so high-bit use could be signed-sensitive, though current callers use small bit positions.

Test signals: compile coverage and register-programming tests that verify individual bit changes preserve unrelated register fields.
