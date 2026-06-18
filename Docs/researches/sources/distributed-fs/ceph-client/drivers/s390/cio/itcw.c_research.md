# sources/distributed-fs/ceph-client/drivers/s390/cio/itcw.c

Purpose: provides an incremental builder for FCX transport command words and associated TCCB, TSB, TIDAW, and optional interrogate structures inside one caller-provided buffer.

Important APIs/types/functions: `struct itcw` tracks the main TCW, optional interrogate TCW, TIDAW counts, and capacities. Exports `itcw_get_tcw()`, `itcw_calc_size()`, `itcw_init()`, `itcw_add_dcw()`, `itcw_add_tidaw()`, `itcw_set_data()`, and `itcw_finalize()`. Internal `fit_chunk()` handles alignment and optional 4K crossing avoidance.

Control flow: callers calculate required size, allocate low-address DMA-capable storage, initialize with read/write operation and optional interrogate support, add DCWs and TIDAWs, optionally override data pointer, and finalize. Initialization lays out ITCW metadata, aligned TCWs, optional interrogate TCW, TIDAW lists, TSBs, and TCCBs. `itcw_add_tidaw()` inserts TTIC TIDAWs when the next TIDAW would land on a new page.

State and persistence behavior: all state is in the supplied buffer and is zeroed by `itcw_init()`. No internal allocation or persistence occurs.

Dependencies and integration points: builds on exported FCX helpers from `fcx.c`, `asm/fcx.h`, `asm/itcw.h`, and s390 DMA/physical address constraints. Used by transport-mode I/O consumers that need safe control-block layout.

Risks and test signals: the 2GB physical limit, 4K boundary handling, TTIC insertion, and capacity accounting are the key risks. Tests should cover undersized buffers, read/write modes, interrogate TCW generation, page-boundary TIDAW insertion, `-ENOSPC`, final count fields, and invalid high physical addresses.
