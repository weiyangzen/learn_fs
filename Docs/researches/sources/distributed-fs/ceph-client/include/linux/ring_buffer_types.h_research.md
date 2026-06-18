# sources/distributed-fs/ceph-client/include/linux/ring_buffer_types.h

Purpose: this companion header defines low-level ring-buffer layout constants shared by tracing ring-buffer internals and headers that need page/event sizing.

Important APIs/types/functions: timestamp constants are `TS_SHIFT`, `TS_MASK`, and `TS_DELTA_TEST`; `test_time_stamp()` checks whether a delta exceeds inline capacity. Layout macros include `BUF_PAGE_HDR_SIZE`, `RB_EVNT_HDR_SIZE`, `RB_ALIGNMENT`, `RB_MAX_SMALL_DATA`, `RB_EVNT_MIN_SIZE`, alignment choices, and `RB_ALIGN_DATA`. `struct buffer_data_page` contains a page timestamp, local commit index, and aligned flexible data area.

Control flow: ring-buffer code uses `test_time_stamp()` to decide whether to emit time-extension records. Page and event header size macros drive allocation, event packing, and read-page formatting.

State and persistence: `buffer_data_page` is the persistent in-memory format for ring-buffer pages: page timestamp, commit offset, and event data. The header itself stores no global state.

Dependencies and integration points: depends on `asm/local.h`, `offsetof`, ring-buffer event type length constants from `ring_buffer.h`, and architecture 64-bit alignment capability.

Risks: layout macros are ABI-like for tracing buffer interpretation; alignment changes can break readers or corrupt event parsing. `test_time_stamp()` must agree with event timestamp encoding. Test signals include ring-buffer page format tests, 32-bit and 64-bit alignment builds, timestamp extension boundary tests, and mmap/read-page compatibility.
