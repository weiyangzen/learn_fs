# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.h

Purpose: central user-space sched_ext support header used by loader programs.

Important APIs/macros: defines fixed-width typedef aliases (`u8`, `u16`, `u32`, `u64`, `s8`, `s16`, `s32`, `s64`), `SCX_BUG()` and `SCX_BUG_ON()` fatal-report macros, and `RESIZE_ARRAY()` for libbpf skeleton data-section resizing that matches BPF-side `RESIZABLE_ARRAY()`.

Control flow: `SCX_BUG()` prints file/line and optional `errno` text, prints a formatted message, then exits. `RESIZE_ARRAY()` sets map value size for a custom data section and refreshes the skeleton pointer with `bpf_map__initial_value()`.

State and persistence: no persistent state. It mutates libbpf skeleton map sizes and initial-value pointers before load.

Dependencies and integration: includes generated enum definitions, user-exit handling, user-space compatibility helpers, enum initialization helpers, and arena stubs. All C loaders in this subset include it either directly or through skeleton workflows.

Risks: `SCX_BUG()` exits immediately and is intended for fatal loader errors. `RESIZE_ARRAY()` must be called before load and must match BPF declarations; incorrect element counts produce malformed data-section expectations.

Test signals: user-space scheduler loader builds, successful skeleton open/load after resizing arrays, and intentional fatal-path checks such as invalid CPU counts or missing BTF.
