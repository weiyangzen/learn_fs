# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.c

## Purpose
`io.c` implements common wlcore bus and address-partition helpers: bus block-size setup, IRQ enable/disable/synchronize wrappers, virtual-to-physical target address translation, partition programming, and optional bus reset/init callbacks.

## Important APIs and functions
`wl1271_set_block_size()` configures the bus block size through `wl->if_ops`. `wlcore_disable_interrupts()`, `wlcore_disable_interrupts_nosync()`, `wlcore_enable_interrupts()`, and `wlcore_synchronize_interrupts()` wrap Linux IRQ APIs. `wlcore_translate_addr()` maps wlcore virtual target addresses into the current physical partition layout. `wlcore_set_partition()` writes the four partition start/size registers through raw IO and updates `wl->curr_part`. `wl1271_io_reset()` and `wl1271_io_init()` call optional bus-level callbacks.

## Control flow
Address translation checks whether an address falls in memory, register, memory2, or memory3 windows and returns a contiguous physical offset. Partition programming copies the requested partition set into `wl->curr_part`, logs each window, then writes hardware partition registers in order. Errors abort remaining writes and return upward.

## State and persistence behavior
The persistent state is `wl->curr_part`, which all translated IO wrappers use until the next partition change. Hardware partition registers persist in the target until reprogrammed or reset. IRQ state is managed by Linux IRQ core, not stored here.

## Dependencies and integration points
This file depends on bus `if_ops`, register constants from `io.h`, debug logging, and Linux IRQ APIs. `cmd.c`, `event.c`, `debugfs.c`, `init.c`, TX/RX paths, and chip-specific code all rely on the partition and raw/translated IO model.

## Risks
Bad partition state can redirect every translated read/write. `wlcore_translate_addr()` warns and returns zero for out-of-range addresses, so callers may accidentally access physical zero after a bad address. Partition programming comments describe wl12xx/wl18xx register conflicts around partition 3, making changes especially risky. IRQ disable variants must be used in the right context to avoid deadlocks or races.

## Test signals
Signals include successful block-size setup, correct register/memory reads after partition changes, no out-of-range warnings during normal command/event/debugfs access, working suspend/resume IO reset/init, and correct IRQ masking behavior during recovery and teardown.
