# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.c

## Purpose

`ras_aca.c` implements rascore Accelerator Check Architecture handling. It reads MCA/ACA banks through MP1 callbacks, matches banks to RAS blocks, parses ECC counts, logs raw register data, updates per-block counters, records bad UMC banks, and exposes ECC query/clear operations.

## Important APIs, Types, And Functions

Public APIs include `ras_aca_sw_init/fini`, `ras_aca_hw_init/fini`, `ras_aca_update_ecc`, `ras_aca_get_block_ecc_count`, `ras_aca_clear_block_new_ecc_count`, `ras_aca_clear_all_blocks_ecc_count`, `ras_aca_mark_fatal_flag`, and `ras_aca_clear_fatal_flag`. Key internals include bank dumping, block matching/parsing, duplicate UE filtering during fatal handling, sequence-number selection, log-ring insertion, bad-bank EEPROM/UMC recording, and per-socket/AID/XCD counter aggregation.

## Control Flow, State, And Persistence

`ras_aca_update_ecc` locks `bank_op_lock`, skips duplicate UE fatal reads, queries bank count, creates a log batch, dumps each bank register array, finds the matching block, parses counts, assigns a CE/UE/DE/poison seqno, logs raw ACA registers, updates counters under `aca_lock`, and records UMC deferred errors to firmware EEPROM or UMC bad-page caches. SW init validates topology bounds and initializes per-block socket/AID/XCD dimensions. HW init selects an IP function table by ACA IP version and binds block info. Persistent state includes per-block accumulated counts, new-count fields, fatal-read mark, log-ring events, EEPROM records, and pending bad-bank lists.

## Dependencies And Integration Points

It depends on rascore MP1 bank dump/count callbacks, `ras_aca_v1_0` block parsers, UMC bad-page logging, firmware EEPROM, log ring, sequence-number APIs, and rascore config topology. It feeds command queries and event processing.

## Risks And Test Signals

Risks include null `aca_blk` use if no block matches, topology bounds errors, duplicate fatal handling hiding real UE data, wrong count aggregation for GFX XCDs, failure to destroy batch tags on errors, and bad-page logging differences between reset and runtime. Test signals include CE/UE/DE bank dump tests, unmatched bank behavior, GFX per-XCD aggregation, fatal duplicate UE tests, UMC deferred bad-page persistence, clear-new and clear-all commands, and unsupported ACA IP handling.
