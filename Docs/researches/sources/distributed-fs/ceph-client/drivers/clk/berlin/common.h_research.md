# sources/distributed-fs/ceph-client/drivers/clk/berlin/common.h

## Purpose
Provides a small shared Berlin descriptor for simple gate clocks used by SoC provider files.

## Important APIs, Types, And Functions
Defines `struct berlin2_gate_data` with `name`, `parent_name`, `bit_idx`, and CCF `flags`.

## Control Flow
No code executes here. `bg2.c` and `bg2q.c` iterate arrays of `berlin2_gate_data` and call `clk_hw_register_gate` for each entry.

## State And Persistence
Gate descriptors are static init-time data. Runtime gate state is stored in SoC clock-enable registers and CCF gate objects.

## Dependencies And Integration Points
Included by Berlin SoC provider files. It complements the divider and PLL helper headers.

## Risks And Edge Cases
The descriptor does not carry a register offset, so users assume all gates in a given array share the SoC file's `REG_CLKENABLE` base. Wrong bit indexes affect unrelated hardware clocks.

## Test Signals
Compile coverage and provider tests verifying each gate name, parent, bit, and ignore-unused flag are sufficient.
