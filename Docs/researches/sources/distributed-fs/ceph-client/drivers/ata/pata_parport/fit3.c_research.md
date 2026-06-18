# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit3.c

## Purpose
Implements the Fidelity International Technology TD-3000 protocol, a newer FIT parallel-port IDE adapter with more transfer modes than FIT2.

## Important APIs, Types, And Functions
`fit3_read_regr()` and `fit3_write_regr()` use data and extended port offset 7 helpers. `fit3_read_block()` and `fit3_write_block()` handle multiple modes, including faster paths. `fit3_connect()`, `fit3_disconnect()`, and `fit3_log_adapter()` handle port state and diagnostics. The `fit3` `pi_protocol` advertises its supported mode range.

## Control Flow
Probe chooses a mode with generic tests. Data and register paths branch on `pi->mode`, using nibble reconstruction for low modes and wider accesses for higher modes.

## State And Persistence
State is limited to saved port registers and the selected mode in `pi_adapter`; no private allocation is used.

## Dependencies And Integration Points
Depends on `pata_parport.h` direct IO macros and core module registration.

## Risks And Edge Cases
The protocol uses nonstandard port offset 7, so resource range assumptions must match the core's EPP/wide-mode validation. Mixed portable disk/CD devices can expose different timing tolerances.

## Test Signals
Mode probing across all supported modes, register echo, block read/write in low and high modes, invalid port-range rejection, and disconnect restore.
