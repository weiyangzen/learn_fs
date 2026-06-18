# sources/distributed-fs/ceph-client/net/xdp/Makefile

Purpose: maps AF_XDP Kconfig symbols to the core and diagnostic object files.

Important build mappings: `CONFIG_XDP_SOCKETS` builds `xsk.o`, `xdp_umem.o`, `xsk_queue.o`, `xskmap.o`, and `xsk_buff_pool.o`; `CONFIG_XDP_SOCKETS_DIAG` builds `xsk_diag.o`.

Control flow: kbuild includes objects in the built-in image or module set according to the symbol values. Core AF_XDP is built as a group, while diag can be a separate loadable module.

State and persistence: no runtime state is owned; this is the persistent build contract for AF_XDP.

Dependencies and integration: must stay synchronized with exports used by drivers (`xsk_*`, `xp_*`), BPF map registration, socket registration, and diag module aliases.

Risks and test signals: missing an object breaks link-time symbol resolution or runtime feature availability. Tests should cover core-only builds, diag module builds, and AF_XDP selftests that exercise UMEM, queue, map, and socket paths.
