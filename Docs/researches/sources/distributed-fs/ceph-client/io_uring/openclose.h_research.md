# sources/distributed-fs/ceph-client/io_uring/openclose.h

Purpose: declares the open/close/pipe/fixed-fd operation interface used by the io_uring opcode dispatch table and resource helpers.

Important APIs/types/functions: prototypes cover `__io_close_fixed()`, prep/issue pairs for `openat`, `openat2`, `close`, `pipe`, and `install_fixed_fd`, plus `io_open_cleanup()` and `io_openat_bpf_populate()`.

Control flow: this header has no runtime control flow; it provides the contract that operation definitions call during SQE prep, issue, and cleanup.

State and persistence: no state is defined here. The visible API implies ownership transfer rules for fixed files and delayed filename cleanup implemented in `openclose.c`.

Dependencies/integration: includes `bpf_filter.h` because open requests can be exposed to io_uring BPF filtering. Other users need `io_ring_ctx`, `io_kiocb`, and `io_uring_sqe` definitions from the wider io_uring type set.

Risks/test signals: header drift would break opcode registration or cleanup hooks. Build coverage is the main signal; behavioral tests live with `openclose.c` and fixed-file resource paths.
