<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.h

## Purpose
`xdp_sample_user.h` declares the userspace API, stat masks, exit codes, skeleton integration macros, and utility helpers for XDP sample applications.

## Important APIs, Types, And Functions
It defines `enum stats_mask`, `EXIT_*` codes, prototypes for sample setup/run/exit/install helpers, `get_driver_name()`, `get_mac_addr()`, `safe_strncpy()`, `__attach_tp()`, `sample_init_pre_load()`, and `DEFINE_SAMPLE_INIT()`.

## Control Flow
Macros drive skeleton consumers: `sample_init_pre_load()` sets `nr_cpus` and configures map sizes before load; `DEFINE_SAMPLE_INIT()` attaches selected tracepoint programs after load based on the stat mask.

## State And Persistence
The header owns no state but defines the contract for shared globals and skeleton maps/links used by `xdp_sample_user.c` and generated skeletons.

## Dependencies And Integration Points
It depends on libbpf skeleton conventions and `xdp_sample_shared.h`. Consumers must have maps and programs with the expected names.

## Risks And Edge Cases
Macro-based skeleton integration fails at compile time or runtime if generated skeleton names differ. `__attach_tp()` returns `-EINVAL` when the program type is not tracing, so consumers must configure sections correctly.

## Test Signals
Successful skeleton samples call `sample_init_pre_load()`, load, then `sample_init()` without error and show attached tracepoint links for requested stat masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.h -->
