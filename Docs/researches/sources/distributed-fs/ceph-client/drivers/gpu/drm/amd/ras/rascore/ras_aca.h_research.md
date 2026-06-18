# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.h

## Purpose

`ras_aca.h` defines generic ACA data structures, topology limits, register indices, ECC counters, block metadata, and the public ACA API.

## Important APIs, Types, And Functions

It defines socket/AID/XCD/block maximums, ACA error masks, `enum ras_aca_reg_idx`, bank register storage, hardware IP IDs, decoded bank info, per-bank/per-count/per-XCD/per-AID/per-socket/per-block ECC state, bank hardware ops, block info, block handle, IP function table, and `struct ras_aca`. Public functions cover SW/HW init/fini, ECC count query/clear, ECC update, and fatal flag mark/clear.

## Control Flow, State, And Persistence

The header has no implementation flow. It defines how ACA state persists inside `ras_core_context`: counters are split into new and total CE/UE/DE counts, GFX can store per-XCD counts, and locks protect counter and bank operations.

## Dependencies And Integration Points

It includes `ras.h` and is consumed by ACA core, ACA v1.0 parsers, command handlers, and manager rascore config. Hardware-specific files populate `aca_block_info` and `ras_aca_ip_func`.

## Risks And Test Signals

Risks include fixed maximums not matching future topology, block IDs used as array indexes, signed `UNKNOWN = -1` handling, and parser callbacks not filling all required bank info. Test signals include topology validation, block-info binding, counter aggregation, and static analysis for array bounds.
