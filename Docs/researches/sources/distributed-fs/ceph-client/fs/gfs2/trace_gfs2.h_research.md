# sources/distributed-fs/ceph-client/fs/gfs2/trace_gfs2.h

## Purpose
`trace_gfs2.h` defines Linux tracepoints for GFS2 glock state, log/journal activity, block mapping, iomap operations, block allocation, and resource reservations. It gives runtime observability for allocator, locking, and log behavior without adding ad hoc logging.

## Important APIs, Types, And Events
The file sets `TRACE_SYSTEM gfs2`, declares symbolic printers for DLM lock states, GFS2 block states, reservation actions, and glock flags, and maps GFS2 lock states to DLM trace values through `glock_trace_state`.

Trace events include `gfs2_glock_state_change`, `gfs2_glock_put`, `gfs2_demote_rq`, `gfs2_promote`, `gfs2_glock_queue`, `gfs2_glock_lock_time`, `gfs2_pin`, `gfs2_log_flush`, `gfs2_log_blocks`, `gfs2_ail_flush`, `gfs2_bmap`, `gfs2_iomap_start`, `gfs2_iomap_end`, `gfs2_block_alloc`, and `gfs2_rs`.

## Control Flow And State Captured
Lock events capture device, glock type/number, current/target/demote states, queue direction, DLM status, and timing statistics. Log events capture pin/unpin, flush start/end, log sequence, reservation counts, and AIL writeback. Mapping events capture inode, logical/physical blocks, iomap range/type/flags, and return codes. Allocator events capture rgrp address, free clone count, requested/reserved counts, allocation state, and reservation range.

## Dependencies And Integration Points
The header includes Linux tracepoint infrastructure plus GFS2 in-core, glock, and rgrp definitions. It must remain in sync with fields used in `glock.c`, `log.c`, `bmap.c`, `rgrp.c`, transaction code, and writeback code. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` inclusion support kernel trace generation.

## Risks And Test Signals
Risks include dereferencing unstable glock/rgrp fields in trace fast paths, format drift that breaks trace consumers, and compile issues when structures change. Signals include successful kernel tracepoint generation, `tracefs` event availability, allocator stress runs showing coherent `gfs2_block_alloc` and `gfs2_rs` sequences, and lock contention tests producing `gfs2_glock_lock_time` data.
