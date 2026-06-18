<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.c

## Purpose
`xdp_sample.bpf.c` provides reusable tracing-side statistics programs for XDP samples. It collects redirect errors, cpumap enqueue/kthread stats, exceptions, and devmap transmit stats into shared maps consumed by userspace.

## Important APIs, Types, And Functions
Maps include `rx_cnt`, `redir_err_cnt`, `cpumap_enqueue_cnt`, `cpumap_kthread_cnt`, `exception_cnt`, `devmap_xmit_cnt`, and `devmap_xmit_cnt_multi`. Programs attach to tp_btf tracepoints such as `xdp_redirect_err`, `xdp_redirect_map_err`, `xdp_redirect`, `xdp_redirect_map`, `xdp_cpumap_enqueue`, `xdp_cpumap_kthread`, `xdp_exception`, and `xdp_devmap_xmit`.

## Control Flow
Tracepoint programs filter by configured `from_match`, `to_match`, or `cpumap_map_id`, compute a per-CPU or pair key, look up the appropriate stats record, and update processed/drop/issue/info counters with no-tear macros. Redirect errors are normalized into errno buckets.

## State And Persistence
Persistent state is all in BPF maps and read-only globals (`nr_cpus`, match arrays) configured before load. Counters accumulate until userspace reads, diffs, or clears them.

## Dependencies And Integration Points
It depends on BTF tracepoint attachment, shared `struct datarec`, and userspace helper setup in `xdp_sample_user.c`/`.h`. It is linked into higher-level samples such as the IPv4 router.

## Risks And Edge Cases
Map sizing is tied to CPU count and expected action/error dimensions; userspace must size maps before load. Duplicate `tp_btf/xdp_devmap_xmit` sections collect aggregate and pairwise stats from the same tracepoint. Filtering arrays treat empty sets as match-all.

## Test Signals
Under XDP redirect/cpumap/devmap activity, corresponding maps should show increasing processed, dropped, issue, and info counters. Userspace summary output should reflect these deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.c -->
