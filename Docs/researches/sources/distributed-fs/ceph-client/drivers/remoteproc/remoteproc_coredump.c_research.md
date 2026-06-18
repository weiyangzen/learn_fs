# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_coredump.c

## Purpose
Builds remoteproc crash dumps as ELF core files and exposes them through Linux devcoredump. It supports full buffered dumps and inline dumps where userspace reads remote memory while recovery waits.

## Important APIs, Types, And Functions
Exports `rproc_coredump_cleanup()`, `rproc_coredump_add_segment()`, `rproc_coredump_add_custom_segment()`, `rproc_coredump_set_elf_info()`, `rproc_coredump()`, and `rproc_coredump_using_sections()`. `struct rproc_coredump_state` keeps the rproc, generated header, and completion used by inline dumps. Dump inputs are `struct rproc_dump_segment` entries on `rproc->dump_segments`, optionally with a custom segment dump callback.

## Control Flow
Drivers register dump segments and optionally set ELF class/machine. On crash recovery, the core calls the coredump op. `rproc_coredump()` sizes the ELF header and program headers, initializes identity and metadata, emits one `PT_LOAD` header per segment, copies data for buffered mode, and calls `dev_coredumpv()`. Inline mode calls `dev_coredumpm()` with `rproc_coredump_read()` and blocks on a completion until devcoredump frees the dump. `rproc_coredump_using_sections()` emits section headers and a string table instead of program headers.

## State And Persistence Behavior
Segment registrations persist on `rproc->dump_segments` until resource cleanup. Buffered dumps transfer the vmalloc buffer to devcoredump. Inline dumps keep only the header buffered and copy segment data from remote memory during reads. Invalid segment translations are logged and filled with `0xff` bytes rather than aborting the whole dump.

## Dependencies And Integration Points
Uses `remoteproc_elf_helpers.h`, `rproc_da_to_va()`, I/O-safe memory copy helpers, completions, vmalloc, and devcoredump. `remoteproc_core.c` installs `rproc_coredump()` as the default coredump op when a platform does not provide one.

## Risks
Inline mode stalls recovery until userspace reads the dump or devcoredump times out. Section-mode assumes `segment->priv` is a valid section-name string. Large segment sets can fail allocation or cause long userspace reads. Translation failures produce incomplete but syntactically present dumps, so consumers must treat `0xff` regions as fault evidence.

## Test Signals
Force crashes with coredump disabled, enabled, and inline; validate ELF headers with `readelf`; test section-mode names; register normal and custom segments; inject invalid device addresses; verify cleanup empties `dump_segments`; and confirm recovery wait behavior differs between buffered and inline modes.
