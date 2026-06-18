# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.h

## Purpose
`user_exp_rcv.h` declares the data structures and public driver entry points for user expected receive support. It describes pinned user buffers, programmed TID nodes, page-set decomposition, and setup/clear/invalidation APIs used by the file/ioctl layer and user SDMA.

## Important APIs and Types
`struct tid_pageset` records a physically contiguous page run as an index and count. `struct tid_user_buf` tracks a setup request: cover interval notifier, mutex, virtual address, length, page count, page array, and flexible page-set list. `struct tid_rb_node` tracks one programmed hardware receive entry: interval notifier, filedata owner, invalidation mutex, physical address, TID group, RcvArray entry, DMA address, freed flag, page count, and flexible page array. `num_user_pages()` computes the number of pages spanned by an address/length range. Public functions are `hfi1_user_exp_rcv_init()`, `hfi1_user_exp_rcv_free()`, `hfi1_user_exp_rcv_setup()`, `hfi1_user_exp_rcv_clear()`, and `hfi1_user_exp_rcv_invalid()`. `mm_from_tid_node()` returns the notifier-owned `mm_struct`.

## Control Flow
The header is consumed by expected receive implementation and by user SDMA for shared TID concepts. A caller initializes per-file expected receive state, submits `hfi1_tid_info` mappings through setup, later clears explicit TIDs, polls invalidated TIDs, and frees all per-file mappings at close.

## State, Persistence, and Dependencies
The header itself stores no state, but its structs define the lifetime contract. `tid_user_buf` is transient during setup, while `tid_rb_node` persists for as long as a TID remains programmed. Dependencies include `hfi.h` for file/context/device types and `exp_rcv.h` for TID encoding and group definitions. MMU interval notifiers are embedded in both transient and persistent structures to detect unmap races.

## Integration Points
`user_exp_rcv.c` owns all function implementations. `user_sdma.h` includes this header because expected SDMA requests carry and validate TID entries. Filedata and context structures in `hfi.h` point to arrays and counters manipulated through these APIs.

## Risks and Test Signals
Risks are ABI-sensitive structure assumptions inside C implementation, flexible-array allocation size errors, and misuse of `num_user_pages()` with zero length or overflowed address ranges. Test signals include compiling with flexible-array bounds checks, setup/clear/invalidation API coverage, and expected SDMA requests using TID lists produced by setup.
