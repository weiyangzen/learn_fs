# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen.h

## Purpose
This header provides small register-field helpers shared by the ST clockgen mux, PLL, and frequency-synthesizer drivers.

## Important APIs, Types, And Functions
`struct clkgen_field` holds an offset, mask, and shift. `clkgen_read()` extracts a field from `base + offset`; `clkgen_write()` updates the field using read-modify-write. `CLKGEN_FIELD()` initializes field metadata. `CLKGEN_READ(pll, field)` and `CLKGEN_WRITE(pll, field, val)` assume the caller object has `regs_base` and `data` members.

## Control Flow
There is no standalone runtime flow. Consumers call the inline helpers in their clock ops while holding any required locks.

## State And Persistence
No state is stored in the header. The helpers read and write hardware register state.

## Dependencies And Integration Points
It declares `extern spinlock_t clkgen_a9_lock`, which is defined in `clkgen-pll.c` and used by A9-related mux/PLL paths. It depends on `readl()` and `writel()` being available via including C files.

## Risks
The write helper does not apply `field->mask` to `val` before shifting, so callers must provide an in-range value. The helpers do not lock; correctness depends on callers using the right spinlock around shared registers.

## Test Signals
Coverage comes indirectly from all ST clockgen drivers. Register field tests should focus on preserving unrelated bits and writing expected shifted field values.
