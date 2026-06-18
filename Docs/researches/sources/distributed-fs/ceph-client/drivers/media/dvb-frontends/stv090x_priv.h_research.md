# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_priv.h

## Purpose
`stv090x_priv.h` is the private implementation contract for `stv090x.c`. It defines logging levels, demod-path register access macros, bitfield manipulation helpers, acquisition thresholds, internal enums for signal/search/delivery/modulation state, lookup-table row types, and the two core runtime state structures.

## Important APIs, Types, And Macros
`dprintk()` gates kernel logging through the module-global `verbose` value. The register access macros `STV090x_READ_DEMOD()` and `STV090x_WRITE_DEMOD()` select P1 or P2 register symbols based on `state->demod`, while `STV090x_ADDR_OFFST()` computes the opposite path address family used by a few shared-register scenarios. `STV090x_SETFIELD()`, `STV090x_GETFIELD()`, `STV090x_SETFIELD_Px()`, and `STV090x_GETFIELD_Px()` encode/decode bitfields using the offset/width macros from `stv090x_reg.h`.

The header defines internal state enums: `stv090x_signal_state` for acquisition results, `stv090x_fec`, `stv090x_modulation`, `stv090x_frame`, `stv090x_pilot`, `stv090x_rolloff`, `stv090x_inversion`, `stv090x_modcod`, `stv090x_search`, `stv090x_algo`, and `stv090x_delsys`. These values are cached in `struct stv090x_state` and many of them mirror hardware register encodings.

Small data types support the implementation’s tables: `struct stv090x_long_frame_crloop`, `struct stv090x_short_frame_crloop`, `struct stv090x_reg`, and `struct stv090x_tab`.

`struct stv090x_internal` represents physical-chip shared state: I2C adapter/address, demod and tuner mutexes, master clock, device cut/version, and reference count. `struct stv090x_state` represents one DVB frontend path and stores device/demod mode, config, frontend, cached delivery/search parameters, signal metadata, tuner bandwidth, search range, and lock timeouts.

## Control Flow And Integration
The implementation relies on this header at every layer. Setup fills `struct stv090x_internal`, attach/probe fill `struct stv090x_state`, register helpers use the path macros, search and tracking functions update the internal enums, and metric/status paths read the cached delivery system and modulation state. The thresholds `STV090x_IQPOWER_THRESHOLD` and `STV090x_SEARCH_AGC2_TH()` guide no-signal and blind-search decisions.

## State And Persistence Behavior
The header itself stores no state, but it defines the persistent in-memory layout used for the lifetime of the frontend. `struct stv090x_internal` can be shared by two `struct stv090x_state` objects; the mutexes in that object serialize shared demod registers and tuner I2C access. `struct stv090x_state` is mutable across tuning operations, so cached fields are both inputs to later operations and outputs from the most recent acquisition.

## Dependencies
It includes `<media/dvb_frontend.h>` and depends on public enums from `stv090x.h` plus register symbols from `stv090x_reg.h` being available in the including C file. The field macros assume every referenced bitfield has matching `STV090x_OFFST_*` and `STV090x_WIDTH_*` definitions.

## Risks And Edge Cases
The bitfield macros do not mask `val` before shifting, so callers must pass values that fit the field width. They also use `1 << width`, so unexpected widths at or above the native int width would be unsafe, though this register file uses small fields. `STV090x_READ_DEMOD()` and `STV090x_WRITE_DEMOD()` choose paths by comparing only with `STV090x_DEMODULATOR_1`; invalid demod values silently map to P1. Logging macro behavior is nonstandard because it compares `verbose > level`, which can make exact level expectations surprising.

## Test Signals
Compile-time coverage is the primary signal: every field macro reference should resolve against `stv090x_reg.h`. Runtime signals include correct P1/P2 register selection for both demodulators, shared mutex behavior on dual-demod hardware, accurate cached state after tuning, correct threshold behavior for no-signal and blind-search cases, and logging controlled by the `verbose` module parameter.
