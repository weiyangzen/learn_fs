# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/trap.h

## Purpose

`trap.h` defines numeric mlxsw hardware trap identifiers for packet traps and asynchronous event traps. These constants are the stable bridge between register/listener programming and higher-level Spectrum trap handling.

## Important APIs, Types, And Functions

The first anonymous enum lists packet trap ids, covering Ethernet control and FDB events, L2 protocols, multicast snooping, sampling, router exceptions, IPv6 control traffic, tunnel decap and NVE ARP, BFD/router alert, discard reasons, ACL traps, and mirror-session trap ids `MLXSW_TRAP_ID_MIRROR_SESSION0` through `MLXSW_TRAP_ID_MIRROR_SESSION7`. `MLXSW_TRAP_ID_MAX` caps packet trap ids at `0x3FF`.

`enum mlxsw_event_trap_id` lists firmware and hardware event ids such as fatal events, port up/down, module plug/unplug, temperature warning, PTP FIFO events, downstream device status, binary code transfer completion, and port mapping changes.

## Control Flow

There is no executable control flow. Other files compile these constants into listener tables and register payloads. For example, `spectrum_trap.c` uses many ids in listener macros, and `spectrum_span.h` documents that SPAN session ids correspond to the mirror-session trap ids in this header.

## State And Persistence

The file defines constants only. The persistence concern is ABI-like stability relative to firmware/hardware trap numbering and devlink trap mapping.

## Dependencies And Integration Points

It has no includes and is consumed by mlxsw core and Spectrum trap/listener code. The constants must match firmware register definitions and register-packing helpers in `reg.h`.

## Risks And Edge Cases

Renumbering or reusing ids would break hardware event interpretation. Mirror-session ids must remain contiguous if session-id arithmetic is used elsewhere. Adding new traps requires matching listener, devlink trap, documentation, and hardware support updates.

## Test Signals

Compile tests catch missing enum names. Runtime signals include successful trap listener registration, expected devlink trap reporting, SPAN mirror-session trap delivery, and correct hardware event dispatch. No local executable tests were run for this research item.
