# sources/distributed-fs/ceph-client/fs/bfs/Kconfig

Purpose: defines configuration for SCO UnixWare BFS filesystem support.

Important APIs/types/functions: `config BFS_FS` is a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`.

Control flow: enabling this option builds the `bfs` driver to read and write UnixWare `/stand` slices.

State and persistence: build-time configuration only.

Dependencies and integration: integrates BFS with block devices, buffer-head I/O, and UnixWare partition usage documented in kernel filesystem docs.

Risks: help text warns this is a niche boot filesystem and should normally be disabled unless needed.

Test signals: Kconfig build coverage as module and built-in; smoke mount of a BFS image.
