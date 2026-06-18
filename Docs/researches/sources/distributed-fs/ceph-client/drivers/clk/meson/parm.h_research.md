# sources/distributed-fs/ceph-client/drivers/clk/meson/parm.h

## Purpose
Provides small bitfield helper macros and accessors used by Meson clock code to describe and manipulate register parameters. It abstracts width/shift-based fields into `struct parm` and inline read/write helpers around regmap.

## Important APIs, Types, And Functions
`PMASK(width)`, `SETPMASK(width, shift)`, and `CLRPMASK(width, shift)` build masks. `PARM_GET(width, shift, reg)` extracts a field from a raw register value, while `PARM_SET(width, shift, reg, val)` returns a raw register value with the field replaced. `MESON_PARM_APPLICABLE(p)` treats non-zero width as field presence. `struct parm` stores `reg_off`, `shift`, and `width`. `meson_parm_read()` reads a register and extracts the field. `meson_parm_write()` updates the field with `regmap_update_bits()`.

## Control Flow
The helpers are inline and synchronous. Callers pass a regmap and parameter descriptor; reads perform one `regmap_read()`, writes perform one masked `regmap_update_bits()`. There is no error propagation from either helper.

## State And Persistence
State lives only in hardware registers. `struct parm` is a descriptor, normally static in clock data. The helpers do not cache values and do not allocate software state.

## Dependencies And Integration Points
Depends on Linux `GENMASK()` through `linux/bits.h` and regmap accessors. Meson PLL and clock helpers can use these descriptors to express register fields without open-coding masks and shifts.

## Risks And Edge Cases
Width must be non-zero and valid for `GENMASK(width - 1, 0)`; a zero-width field is only safe when guarded by `MESON_PARM_APPLICABLE`. `PARM_SET` does not mask `val` before shifting, so callers must pass a value that fits the field width. Read/write helpers ignore regmap return codes, which can hide bus or MMIO access failures.

## Test Signals
Compile all users with sparse and W=1 warnings. Unit-style validation can exercise representative widths/shifts and verify `PARM_GET`/`PARM_SET` round trips. Runtime confidence comes from clock rate programming that uses parm descriptors and from regmap debug confirming only intended bits change.
