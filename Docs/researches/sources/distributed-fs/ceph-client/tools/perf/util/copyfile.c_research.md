# sources/distributed-fs/ceph-client/tools/perf/util/copyfile.c

Purpose: copies files for perf utilities, including namespace-aware source access, temporary destination handling, mode setting, and mmap offset copying.

Important APIs/functions: exports `copyfile`, `copyfile_mode`, `copyfile_ns`, and `copyfile_offset`; internal `slow_copyfile` handles zero-size/proc-like files.

Control flow: stats source in the requested namespace, creates a hidden temp file near the destination, uses slow text copy for zero-size sources or mmap+pwrite for regular files, sets mode, links temp to final destination, unlinks temp, and closes fds.

State and persistence: writes destination files via temporary sibling paths; no global state beyond util `page_size`.

Dependencies and integration: namespace helpers, mmap, stat/open/link/unlink, internal page size, and Linux types. Used by build-id and file cache code.

Risks: `copyfile_offset` unmap length depends on mutated variables and is fragile. `link(tmp, to)` fails if destination exists. Slow copy is line based and may not suit binary virtual files.

Test signals: regular, empty, proc-like, existing destination, interrupted writes, non-page offsets, large files, namespace sources, and mode propagation.
