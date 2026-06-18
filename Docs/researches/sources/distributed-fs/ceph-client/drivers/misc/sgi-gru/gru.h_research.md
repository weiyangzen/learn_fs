# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru.h

Purpose: public-ish GRU architectural and userspace option header defining cacheline/handle offsets, GSEG mapping page size, chiplet info, per-context statistics, and TLB-miss handling options.

Important APIs and types: defines `GRU_CACHE_LINE_BYTES`, `GRU_HANDLE_STRIDE`, `GRU_CB_BASE`, `GRU_DS_BASE`, x86-only `GRU_GSEG_PAGESIZE`, `struct gru_chiplet_info`, `struct gru_gseg_statistics`, and `GRU_OPT_MISS_*` option bits.

Control flow and integration: no functions; constants are consumed by file mmap/ioctls, instruction helpers, and userspace libraries. It enforces x86_64-only builds with `#error` otherwise.

State and persistence: no runtime state.

Dependencies and risks: ABI-sensitive constants define the memory layout expected by userspace and hardware. Tests should compile on supported x86_64 UV configs and ensure userspace tools agree on GSEG size, CB/DS offsets, and option bit semantics.
