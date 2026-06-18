# sources/distributed-fs/glusterfs/xlators/meta/src/mallinfo-file.c

## Purpose
Implements a meta virtual file exposing allocator `mallinfo` information.

## Important APIs, Types, and Functions
- `mallinfo_file_fill()` calls `gf_proc_dump_mallinfo(strfd)`.
- `mallinfo_file_ops` exposes `.file_fill`.
- `meta_mallinfo_file_hook()` attaches ops.

## Control Flow
Read calls the dump helper and returns `strfd->size`.

## State and Persistence
Reads allocator/process memory state; no mutation.

## Dependencies and Integration Points
Depends on GlusterFS proc dump support and strfd.

## Risks
Allocator-specific data may be unavailable or platform-dependent behind `gf_proc_dump_mallinfo()`.

## Test Signals
Reading the meta mallinfo file should produce allocator stats on supported platforms.
