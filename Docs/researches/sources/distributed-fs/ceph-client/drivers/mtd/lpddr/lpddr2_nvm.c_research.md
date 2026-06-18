<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr2_nvm.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr2_nvm.c

Purpose: platform MTD driver for LPDDR2-NVM PCM memories. It maps the memory array plus controller registers, verifies the PFOW overlay window, and provides MTD read, write, erase, lock, and unlock operations.

Important APIs, types, and functions: `struct pcm_int_data` stores controller MMIO and bus width. Helpers `ow_enable()`, `ow_disable()`, `ow_reg_add()`, `lpddr2_nvm_do_op()`, and `lpddr2_nvm_do_block_op()` implement overlay-window command execution. MTD callbacks are `lpddr2_nvm_read()`, `lpddr2_nvm_write()`, `lpddr2_nvm_erase()`, `lpddr2_nvm_lock()`, and `lpddr2_nvm_unlock()`. `lpddr2_nvm_probe()` builds `map_info` and `mtd_info`.

Control flow: probe allocates private structures, maps memory resource 0 as the array and resource 1 as controller registers, initializes a simple map, populates erase/write sizes, verifies PFOW by reading `P`, `F`, `O`, `W`, and registers the MTD. Reads copy directly from the mapped array. Writes enable OW, choose single-word overwrite for unaligned addresses and buffer overwrite for aligned chunks, poll status until OK, then disable OW. Block operations iterate erase-size chunks for erase/lock/unlock.

State and persistence: persistent state is PCM contents and lock status in device hardware. Runtime state is the global `lpdd2_nvm_mutex`, overlay window enable state, and mapped controller registers.

Dependencies and integration points: uses platform resources, `simple_map_init()`, MTD map APIs, MTD partition registration, and ARM relaxed IO helpers.

Risks: `lpddr2_nvm_do_op()` polls without a timeout, so a stuck device can hang the caller. Bus width is hard-coded to x32 constants. The file contains an extra stray comment opener before PFOW verification, but it does not alter behavior in the viewed text. Test signals are PFOW detection, correct resource ordering, unaligned and buffered writes, erase/lock/unlock over multi-block ranges, and failure behavior when status reports errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr2_nvm.c -->
