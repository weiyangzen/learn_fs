<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_priv.h

## Purpose
`stb0899_priv.h` defines the internal state model, algorithm status enums, bitfield helpers, debug macro, and cross-file prototypes for the STB0899 driver. It connects the main driver, algorithm file, and register map.

## Important APIs, Types, And Functions
The file defines debug levels and `dprintk()`, scalar helpers (`GETBYTE`, `MAKEWORD32`, `STB0899_GETFIELD`, `STB0899_SETFIELD_VAL`), `enum stb0899_status`, DVB-S2 `enum stb0899_modcod`, frame and rolloff enums, interpolation table type `struct stb0899_tab`, S1 FEC enum values, requested-parameter cache `struct stb0899_params`, dynamic demod state `struct stb0899_internal`, and top-level `struct stb0899_state`. It declares register accessors, S2 indirect I/O, I2C gate control, DVB-S/DVB-S2 algorithms, and carrier-width calculation.

## Control Flow
`stb0899_drv.c` allocates and owns `struct stb0899_state`, then both the driver and algorithm routines mutate `state->internal` while using the declared helpers. The macro `STB0899_READ_S2REG()` assumes a local variable named `state`, so it is tightly coupled to call-site naming.

## State And Persistence
`struct stb0899_internal` is the core persistent software state for search and readback: clocks, frequencies, symbol rate, FEC/modcod, search geometry, tuner offsets/bandwidth, rolloff, derotator settings, AGC timings, lock/status, DVB-S2 UWP/CSM/FEC attributes, and cached error/status registers. `struct stb0899_state` also stores config, frontend, current delivery system, requested params, DiSEqC receiver frequency, and a search mutex.

## Dependencies And Integration Points
The header depends on DVB frontend types and `stb0899_drv.h`. It is private to the STB0899 implementation but exports prototypes across the split C files.

## Risks And Test Signals
Bitfield macros assume valid widths and may overflow if used with 32-bit-wide fields in inappropriate expressions. `STB0899_READ_S2REG()`'s hidden `state` dependency is error-prone. The search mutex exists but is not visibly used by search in the read code, so concurrent access should be audited. Test signals are clean compilation across C files, correct field extraction/set behavior for representative registers, and stable state transitions after repeated tune/fail/retune cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_priv.h -->
