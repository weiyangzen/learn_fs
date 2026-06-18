# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_defs.h

## Purpose
`stv0367_defs.h` is the static register-default database for the STV0367 driver. It defines the table format, table selectors, generic terrestrial/cable defaults, Digital Devices OFDM/QAM/base defaults, and the combined `stv0367_deftabs` lookup used by `stv0367.c`.

## Important APIs, Types, and Functions
- Table selectors: `STV0367_DEFTAB_GENERIC`, `STV0367_DEFTAB_DDB`, `STV0367_TAB_TER`, `STV0367_TAB_CAB`, `STV0367_TAB_BASE`, and max constants.
- `struct st_register` pairs a 16-bit register address with an 8-bit value.
- Default arrays: `def0367ter[]`, `def0367cab[]`, `def0367dd_ofdm[]`, `def0367dd_qam[]`, and `def0367dd_base[]`.
- `stv0367_deftabs[STV0367_DEFTAB_MAX][STV0367_TAB_MAX]` maps a default-table family and mode to the relevant register array; generic base is `NULL`, DDB base is present.

## Control Flow
This header has no executable logic beyond static data initialization. `stv0367_write_table()` in `stv0367.c` walks a selected array until it reaches `{0x0000, 0x00}` and writes each register/value pair over I2C.

## State and Persistence Behavior
The arrays are compile-time constants. They define the reset/programming baseline that hardware receives during init/reinit. No runtime mutation occurs.

## Dependencies and Integration Points
The header depends on `stv0367_regs.h` for `R367TER_*` and `R367CAB_*` addresses. It is directly included by `stv0367.c`, not a standalone public API. Values encode board-family assumptions such as generic xc5000-related comments and Digital Devices Cine/Flex settings.

## Risks and Edge Cases
- Table termination relies on register address `0x0000` as sentinel; a real need to write address zero would be impossible through this format.
- The header contains large static arrays, so including it outside one C file would duplicate data.
- Register defaults are hardware- and board-sensitive; incorrect table selection can break clocking, ADC, AGC, TS output, or acquisition.
- `stv0367_deftabs` permits `NULL` base table for generic mode, so callers must check before writing base tables; DDB init does this.

## Test Signals
Validation should compare default tables against known-good register dumps for generic and DDB boards. Init tests should verify sentinel termination, table selection, no out-of-bounds table indices, and expected writes for terrestrial, cable, and base setup.
