# sources/distributed-fs/glusterfs/xlators/meta/src/meminfo-file.c

## Purpose
Implements a meta virtual file exposing GlusterFS memory accounting information.

## Important APIs, Types, and Functions
- `meminfo_file_fill()` calls `gf_proc_dump_mem_info_to_dict(strfd)`.
- `meminfo_file_ops` exposes `.file_fill`.
- `meta_meminfo_file_hook()` attaches ops.

## Control Flow
Read dumps memory accounting into the strfd.

## State and Persistence
Reads process memory accounting state; no mutation.

## Dependencies and Integration Points
Depends on GlusterFS proc dump/memory accounting and meta file-fill support.

## Risks
Output can be large and depends on memory accounting initialization in all translators.

## Test Signals
Reading meta meminfo should include translator allocation categories such as trash/upcall/utime when loaded.
