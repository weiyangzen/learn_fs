# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.c

## Purpose
Provides shared FMan storage/profile helpers for buffer-pool ordering and packet buffer-prefix layout. These helpers are used by FMan ports before programming BMI buffer and internal-context registers.

## Important APIs, Types, and Functions
Exports `fman_sp_set_buf_pools_in_asc_order_of_buf_sizes` and `fman_sp_build_buffer_struct`. The first builds an ordered pool-ID array and a size-by-pool-ID array from `struct fman_ext_pools`. The second derives `struct fman_sp_int_context_data_copy`, `struct fman_sp_buf_margins`, and `struct fman_sp_buffer_offsets` from `struct fman_buffer_prefix_content`.

## Control Flow and State
Pool ordering uses insertion-sort-like placement by pool size and writes caller-provided arrays. Buffer layout aligns private data to 16-byte internal context units, initializes parser/timestamp/hash offsets to `ILLEGAL_BASE`, computes copy size for parser results and timestamp/hash context, sets external offsets for each requested metadata item, computes start margin, and aligns the final data offset to the requested alignment. The file keeps no persistent state.

## Dependencies and Integration Points
Depends on `fman_sp.h` and `fman.h` for FMan pool and prefix structures. `fman_port_init` calls both helpers before programming Rx external buffer pools and BMI internal context registers. Consumers later use the computed offsets through `fman_port_get_hash_result_offset` and `fman_port_get_tstamp`.

## Risks and Test Signals
Risks include division/modulo by an invalid zero `data_align`, incorrect assumptions about parser result and timestamp/hash sizes, pool IDs indexing beyond caller arrays, and mismatch between computed margins and actual external buffer sizes. Test signals are Rx initialization with multiple external pool sizes, prefix combinations for parser result/timestamp/hash result, timestamp extraction from received data, and rejection of too-small external buffers in the caller.
