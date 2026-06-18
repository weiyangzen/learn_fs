# sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.h Research

## Purpose
`ms_block.h` defines the private data structures, constants, boot-page layouts, state enums, and debug helpers used by the legacy MemoryStick block driver in `ms_block.c`.

## Important APIs, Types, And Functions
Key constants include `MS_BLOCK_MAX_SEGS`, `MS_BLOCK_MAX_PAGES`, `MS_BLOCK_MAX_BOOT_ADDR`, `MS_BLOCK_BOOT_ID`, `MS_BLOCK_INVALID`, `MS_MAX_ZONES`, and `MS_BLOCKS_IN_ZONE`. Error and OOB helper masks group memstick status/interrupt/overwrite/management bits. Packed on-card layout types include `struct ms_boot_header`, `struct ms_system_item`, `struct ms_system_entry`, `struct ms_boot_attr_info`, `struct ms_cis_idi`, and `struct ms_boot_page`. `struct msb_data` is the central runtime object shared by the FTL, request queue, cache, state machines, and block disk. Enums define legal state values for read-page, write-block, simple-command, reset, and parallel-switch handlers.

## Control Flow
The header does not execute code, but it controls the state-machine topology used by `ms_block.c`. Each enum value corresponds to a switch branch in a `h_msb_*` callback. `struct msb_data` fields connect probe initialization, FTL scanning, blk-mq processing, memstick TPC callbacks, cache timers, and suspend/remove handling.

## State And Persistence
The packed boot structures mirror persistent MemoryStick boot metadata read from flash. `struct msb_data` is volatile per-card state and stores pointers to persistent metadata copies (`boot_page`) and reconstructed in-memory indexes (`lba_to_pba_table`, used/erased bitmaps, free counts). The header’s sentinel values, especially `MS_BLOCK_INVALID`, define how erased/free or unmapped locations are represented.

## Dependencies And Integration Points
It depends on memstick core declarations for register/status constants and types such as `struct ms_register`, `struct ms_register_addr`, and `struct memstick_dev`. It also exposes block-layer and kernel infrastructure fields through `gendisk`, `request_queue`, `blk_mq_tag_set`, `hd_geometry`, scatterlists, workqueues, timers, and spinlocks.

## Risks
The header fixes `MS_MAX_ZONES` at 16 while the runtime computes `zone_count` from card block count; unsupported larger media could overflow `free_block_count`. Packed structures must remain byte-accurate against card format, and endian conversion must be performed by the C file before normal use. The include guard name `MS_BLOCK_NEW_H` is historical and easy to confuse with a public API.

## Test Signals
Compile coverage with `CONFIG_MEMSTICK` and `CONFIG_MEMSTICK_UNSAFE_RESUME` toggles is important. Runtime tests should validate parsed boot attributes, zone counts, invalid-block sentinels, all state-machine transitions, and debug output gating through the `debug` module parameter.
