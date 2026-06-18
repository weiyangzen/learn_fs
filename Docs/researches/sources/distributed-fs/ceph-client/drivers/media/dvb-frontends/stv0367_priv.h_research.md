# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_priv.h

## Purpose
`stv0367_priv.h` provides private macros, byte helpers, and internal enums/structs shared by `stv0367.c` for terrestrial and cable acquisition state classification.

## Important APIs, Types, and Functions
- Boolean and utility macros: `TRUE`, `FALSE`, `NULL`, `MAX`, `MIN`, `INRANGE`, `MAKEWORD`, `LSB`, `MSB`, and `MMSB`.
- Terrestrial enums: `stv0367_ter_signal_type`, `stv0367_ts_mode`, `stv0367_clk_pol`, `stv0367_ter_bw`, `stv0367_ter_mode`, `stv0367_ter_hierarchy`, `stv0367_ter_if_iq_mode`, and `stv0367_ter_force`.
- Cable enums: `stv0367cab_mod` and `stv0367_cab_signal_type`.
- `struct stv0367_cab_signal_info` describes lock, frequency, symbol rate, modulation, inversion, RF power, C/N, and BER fields for cable monitoring-style data.

## Control Flow
The header has no runtime control flow. Its enum values are used by `stv0367.c` switch statements, status mapping, and config interpretation.

## State and Persistence Behavior
No state is stored here. The enums define values persisted in `stv0367ter_state` and `stv0367cab_state` during frontend lifetime.

## Dependencies and Integration Points
This is a private header for the STV0367 implementation. Public board configuration in `stv0367.h` uses integer fields that are expected to correspond to `stv0367_ts_mode`, `stv0367_clk_pol`, and `stv0367_ter_if_iq_mode` values defined here.

## Risks and Edge Cases
The header redefines `NULL` if not already defined and defines `MAX` only inside `#ifndef MIN`, which can produce surprising macro availability depending on prior includes. Several historical enums are inside `#if 0`, so maintainers must avoid relying on commented-out types. Public config fields are not strongly typed to these enums.

## Test Signals
Compile-time coverage should catch macro conflicts with kernel headers. Runtime validation should exercise all enum-backed config values and acquisition result mappings, especially cable FSM state to `FE_HAS_*` status conversion.
