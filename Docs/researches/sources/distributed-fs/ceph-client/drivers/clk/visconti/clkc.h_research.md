<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.h

## Purpose

`clkc.h` defines common data structures for Toshiba Visconti clock-controller helpers.

## Important APIs, Types, And Functions

It declares `struct visconti_clk_provider`, `struct visconti_clk_gate_table`, `struct visconti_fixed_clk`, and runtime `struct visconti_clk_gate`. It also declares `visconti_init_clk()` and `visconti_clk_register_gates()`. `NO_RESET` marks gate entries not associated with reset lines.

## Control Flow

There is no executable flow. TMPV770x table files fill these structures and common helpers consume them.

## State And Persistence Behavior

Only type definitions appear here. Runtime state fields include regmap, onecell data, gate offsets, reset offsets, and shared spinlock pointers.

## Dependencies And Integration Points

It includes syscon, CCF, OF, regmap, spinlock, and `reset.h`, making it the internal bridge between clock and reset helpers.

## Risks And Test Signals

Risks are type-width truncation for flags/IDs and `NO_RESET` being `0xFF` in a `u8`. Build tests catch API drift; runtime tests should validate every table row registers at the intended binding ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.h -->
