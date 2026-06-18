<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.c

## Purpose
`xdp_sample_user.c` is the shared userspace statistics and lifecycle library for XDP samples. It sets up counter maps, collects per-CPU and pairwise records, computes rates, prints summaries, installs/removes XDP programs, handles signals, and provides utility helpers for driver and MAC lookup.

## Important APIs, Types, And Functions
Public APIs include `sample_setup_maps()`, `__sample_init()`, `sample_install_xdp()`, `sample_exit()`, `sample_run()`, `sample_switch_mode()`, `sample_usage()`, `get_driver_name()`, and `get_mac_addr()`. Internal flows include map collection helpers, stats calculations, `sample_timer_cb()`, and `sample_signal_cb()`.

## Control Flow
Initialization records requested stat masks, possible CPU count, signal fd, and map metadata. `sample_setup_maps()` sizes mmapable maps according to stat dimensions. `sample_run()` creates a timerfd, allocates current/previous snapshots, collects initial stats, then polls signal and timer fds. On each timer, it swaps snapshots, collects maps, computes rates, updates summaries, and prints terse or verbose output. `sample_exit()` removes installed XDP programs and prints a final summary.

## State And Persistence
Global state tracks sample maps, mmap pointers, map entry counts, installed XDP program descriptors, log level, interval, signal fd, output totals, CPU count, and requested mask. Kernel state includes attached XDP programs and BPF stats maps.

## Dependencies And Integration Points
It depends on libbpf, BPF mmapable maps, timerfd/signalfd, poll, ethtool/ioctl, locale formatting, Linux hlist/hash utilities, and `xdp_sample_user.h`. It is used by sample skeleton-based tools such as `xdp_router_ipv4_user.c`.

## Risks And Edge Cases
The code is a shared support layer with many global variables, so consumers must call setup in the expected order. Map dimensions must match BPF-side `nr_cpus` and stat masks. Signal handling toggles output mode at runtime. Driver and MAC lookup rely on ioctl support and interface stability.

## Test Signals
Sample consumers should show correct per-second rates, expanded error details on failures, mode switching with SIGQUIT, cleanup of attached XDP programs on exit, and final summary totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.c -->
