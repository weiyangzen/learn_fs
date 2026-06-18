# subset-b-006809 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind4_prog.c

## Purpose

Cgroup IPv4 bind selftest program that rewrites bind addresses/ports, exercises SO_BINDTODEVICE and SO_REUSEPORT manipulation, and provides an explicit deny hook.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/bind4`, `cgroup/bind4`, `license`
- Important functions/callbacks: `bind_v4_prog`, `bind_v4_deny_prog`
- BPF helpers/kfunc-like calls: `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `string.h`, `linux/stddef.h`, `linux/bpf.h`, `linux/in.h`, `linux/in6.h`, `linux/if.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`, `bind_prog.h`. Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly. Helper availability and license restrictions matter for `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind6_prog.c

## Purpose

Cgroup IPv6 bind selftest program that rewrites bind addresses/ports, exercises SO_BINDTODEVICE and SO_REUSEPORT manipulation, and provides an explicit deny hook.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/bind6`, `cgroup/bind6`, `license`
- Important functions/callbacks: `bind_v6_prog`, `bind_v6_deny_prog`
- BPF helpers/kfunc-like calls: `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `string.h`, `linux/stddef.h`, `linux/bpf.h`, `linux/in.h`, `linux/in6.h`, `linux/if.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`, `bind_prog.h`. Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly. Helper availability and license restrictions matter for `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind6_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_perm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_perm.c

## Purpose

Small cgroup bind permission program that allows only bind requests targeting the selftest port for both IPv4 and IPv6.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/bind4`, `cgroup/bind6`, `license`
- Important functions/callbacks: `bind_prog`, `bind_v4_prog`, `bind_v6_prog`
- BPF helpers/kfunc-like calls: `bpf_htons`

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `linux/stddef.h`, `linux/bpf.h`, `sys/types.h`, `sys/socket.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly. Helper availability and license restrictions matter for `bpf_htons`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_perm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_prog.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_prog.h

## Purpose

Shared constants for cgroup bind selftests, defining the target port range and interface index used by IPv4 and IPv6 bind hooks.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_prog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bloom_filter_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bloom_filter_bench.c

## Purpose

BPF bloom-filter map selftest/benchmark program that measures or verifies bloom lookup/update behavior against array/hash map control data.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `.maps`
- Maps: `array_map`, `bloom_map`, `hashmap`
- Important functions/callbacks: `log_result`, `bloom_callback`, `bloom_lookup`, `bloom_update`, `bloom_hashmap_lookup`
- BPF helpers/kfunc-like calls: `bpf_for_each_map_elem`, `bpf_get_prandom_u32`, `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_map_peek_elem`, `bpf_map_push_elem`
- Mutable globals/test result fields: `rand_vals[2500000]`, `nr_rand_bytes`, `hit_key`, `drop_key`, `false_hit_key`, `value_size`, `hashmap_use_bloom`, `count_false_hits`, `error`

## Control Flow and Data Flow

User space seeds maps and globals, then BPF code performs map iteration or direct lookup/update helper calls. Bench variants run callbacks repeatedly and accumulate hit/error counters; correctness variants compare bloom presence with backing maps.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `array_map`, `bloom_map`, `hashmap` Globals are used as userspace-visible configuration/results: `rand_vals[2500000]`, `nr_rand_bytes`, `hit_key`, `drop_key`, `false_hit_key`, `value_size`, `hashmap_use_bloom`, `count_false_hits`, `error`

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `stdbool.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`. Depends on bloom-filter, array, queue/stack, and hash map helper support plus the userspace benchmark harness.

## Risks and Edge Cases

Bloom filters allow false positives by design, so tests must separate expected false-hit accounting from hard lookup failures. Helper availability and license restrictions matter for `bpf_for_each_map_elem`, `bpf_get_prandom_u32`, `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_map_peek_elem`, `bpf_map_push_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `rand_vals[2500000]`, `nr_rand_bytes`, `hit_key`, `drop_key`, `false_hit_key`, `value_size`, `hashmap_use_bloom`, `count_false_hits` to confirm the exercised path ran. Map contents/counts for `array_map`, `bloom_map`, `hashmap` provide state validation. Benchmarks should show successful update/lookup paths and bounded false-hit counts while control hash/array maps remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bloom_filter_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bloom_filter_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bloom_filter_map.c

## Purpose

BPF bloom-filter map selftest/benchmark program that measures or verifies bloom lookup/update behavior against array/hash map control data.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `.maps`
- Maps: `map_random_data`, `map_bloom`, `outer_map`
- Important functions/callbacks: `check_elem`, `inner_map`, `check_bloom`
- BPF helpers/kfunc-like calls: `bpf_for_each_map_elem`, `bpf_map_lookup_elem`, `bpf_map_peek_elem`
- Mutable globals/test result fields: `error`

## Control Flow and Data Flow

User space seeds maps and globals, then BPF code performs map iteration or direct lookup/update helper calls. Bench variants run callbacks repeatedly and accumulate hit/error counters; correctness variants compare bloom presence with backing maps.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `map_random_data`, `map_bloom`, `outer_map` Globals are used as userspace-visible configuration/results: `error`

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`. Depends on bloom-filter, array, queue/stack, and hash map helper support plus the userspace benchmark harness.

## Risks and Edge Cases

Bloom filters allow false positives by design, so tests must separate expected false-hit accounting from hard lookup failures. Helper availability and license restrictions matter for `bpf_for_each_map_elem`, `bpf_map_lookup_elem`, `bpf_map_peek_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `error` to confirm the exercised path ran. Map contents/counts for `map_random_data`, `map_bloom`, `outer_map` provide state validation. Benchmarks should show successful update/lookup paths and bounded false-hit counts while control hash/array maps remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bloom_filter_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_arena_spin_lock.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_arena_spin_lock.h

## Purpose

Header-only BPF arena spinlock implementation that tests low-level atomic locking, IRQ/preemption helpers, and verifier range constraints.

## Important APIs, Types, and Functions

- Important functions/callbacks: `encode_tail`, `xchg_tail`, `clear_pending`, `clear_pending_set_locked`, `set_locked`, `arena_fetch_set_pending_acquire`, `arena_spin_trylock`, `arena_spin_lock_slowpath`, `arena_spin_lock`, `arena_spin_unlock`
- BPF helpers/kfunc-like calls: `bpf_assert_range`, `bpf_get_smp_processor_id`, `bpf_local_irq_restore`, `bpf_local_irq_save`, `bpf_preempt_disable`, `bpf_preempt_enable`, `bpf_printk`

## Control Flow and Data Flow

Lock acquisition first tries an atomic fast path, then sets pending state, exchanges queue tail, disables preemption/IRQs where required, waits through a queued slow path, and releases by clearing lock/pending state or handing off to the next waiter.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_atomic.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_assert_range`, `bpf_get_smp_processor_id`, `bpf_local_irq_restore`, `bpf_local_irq_save`, `bpf_preempt_disable`, `bpf_preempt_enable`, `bpf_printk`.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_arena_spin_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c

## Purpose

Compact CUBIC-like TCP congestion-control struct_ops test that exercises callback registration and pacing/cwnd helper logic.

## Important APIs, Types, and Functions

- BPF sections: `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`, `license`
- Important functions/callbacks: `div64_u64`, `tcp_update_pacing_rate`, `tcp_cwnd_reduction`, `tcp_may_raise_cwnd`, `BPF_PROG`, `bpf_cubic_init`, `bpf_cubic_cwnd_event_tx_start`, `bpf_cubic_cong_control`, `bpf_cubic_recalc_ssthresh`, `bpf_cubic_state`, `bpf_cubic_acked`, `bpf_cubic_undo_cwnd`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance.

## Test Signals

Load/attach success and verifier log expectations are primary signals. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_compiler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_compiler.h

## Purpose

Compiler-attribute compatibility header used by BPF selftest sources to express inline, weak, used, and other compiler-specific annotations.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Integrated through the kernel BPF selftest build and libbpf skeleton loading path.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cubic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cubic.c

## Purpose

Large BPF CUBIC congestion-control implementation adapted from kernel TCP CUBIC for struct_ops selftests.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `bictcp_reset`, `div64_u64`, `fls64`, `bictcp_clock_us`, `bictcp_hystart_reset`, `BPF_PROG`, `cubic_root`, `bictcp_update`, `hystart_ack_delay`, `hystart_update`, `bpf_cubic_init`, `bpf_cubic_cwnd_event_tx_start`, `bpf_cubic_cong_avoid`, `bpf_cubic_recalc_ssthresh`, `bpf_cubic_state`, `bpf_cubic_acked`, `bpf_cubic_undo_cwnd`
- BPF helpers/kfunc-like calls: `bpf_setsockopt`
- Mutable globals/test result fields: `nodelay_init_reject`, `nodelay_cwnd_event_tx_start_reject`, `bpf_cubic_acked_called`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `nodelay_init_reject`, `nodelay_cwnd_event_tx_start_reject`, `bpf_cubic_acked_called` TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_tracing.h`, `errno.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance. Helper availability and license restrictions matter for `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nodelay_init_reject`, `nodelay_cwnd_event_tx_start_reject`, `bpf_cubic_acked_called` to confirm the exercised path ran. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cubic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp.c

## Purpose

BPF implementation of DCTCP congestion-control callbacks, using socket storage and TCP helpers to validate struct_ops behavior.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`, `.struct_ops`
- Maps: `sk_stg_map`
- Important functions/callbacks: `dctcp_reset`, `BPF_PROG`, `dctcp_react_to_loss`, `dctcp_ece_ack_cwr`, `dctcp_ece_ack_update`, `bpf_dctcp_init`, `bpf_dctcp_ssthresh`, `bpf_dctcp_update_alpha`, `bpf_dctcp_state`, `bpf_dctcp_cwnd_event`, `bpf_dctcp_cwnd_undo`, `bpf_dctcp_cong_avoid`
- BPF helpers/kfunc-like calls: `bpf_dctcp_init`, `bpf_getsockopt`, `bpf_setsockopt`, `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_tcp_send_ack`
- Mutable globals/test result fields: `cc_res[TCP_CA_NAME_MAX]`, `tcp_cdg_res`, `stg_result`, `ebusy_cnt`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sk_stg_map` Globals are used as userspace-visible configuration/results: `cc_res[TCP_CA_NAME_MAX]`, `tcp_cdg_res`, `stg_result`, `ebusy_cnt` TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance. Helper availability and license restrictions matter for `bpf_dctcp_init`, `bpf_getsockopt`, `bpf_setsockopt`, `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_tcp_send_ack`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `cc_res[TCP_CA_NAME_MAX]`, `tcp_cdg_res`, `stg_result`, `ebusy_cnt` to confirm the exercised path ran. Map contents/counts for `sk_stg_map` provide state validation. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp_release.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp_release.c

## Purpose

Minimal TCP congestion-control struct_ops program used to exercise release-time cleanup of a BPF TCP congestion-control implementation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `dctcp_nouse_release`
- BPF helpers/kfunc-like calls: `bpf_setsockopt`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance. Helper availability and license restrictions matter for `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp_release.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_flow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_flow.c

## Purpose

BPF flow dissector selftest that parses Ethernet, IPv4, IPv6, GRE, VLAN, MPLS, TCP, UDP, and fragmentation paths through tail calls.

## Important APIs, Types, and Functions

- BPF sections: `flow_dissector`, `.maps`, `.maps`, `flow_dissector`, `license`
- Maps: `jmp_table`, `last_dissection`
- Important functions/callbacks: `export_flow_keys`, `parse_eth_proto`, `_dissect`, `parse_ip_proto`, `parse_ipv6_proto`
- BPF helpers/kfunc-like calls: `bpf_flow_dissect_get_header`, `bpf_htonl`, `bpf_htons`, `bpf_map_update_elem`, `bpf_skb_load_bytes`, `bpf_tail_call_static`

## Control Flow and Data Flow

The root flow dissector dispatches by ethertype through a prog-array tail-call table. Parser stages advance `thoff`, handle encapsulation/fragmentation, fill `struct bpf_flow_keys`, export the last dissection to a hash map, and return OK, DROP, or CONTINUE.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `jmp_table`, `last_dissection`

## Dependencies and Integration Points

Includes `limits.h`, `stddef.h`, `stdbool.h`, `string.h`, `linux/pkt_cls.h`, `linux/bpf.h`, `linux/in.h`, `linux/if_ether.h`, `linux/icmp.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/tcp.h`, and 7 more.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_flow_dissect_get_header`, `bpf_htonl`, `bpf_htons`, `bpf_map_update_elem`, `bpf_skb_load_bytes`, `bpf_tail_call_static`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `jmp_table`, `last_dissection` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_flow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_gotox.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_gotox.c

## Purpose

Verifier/JIT control-flow stress test for gotol/gotox-style branches, switch lowering, jump tables, static globals, and cross-section jumps.

## Important APIs, Types, and Functions

- BPF sections: `.data`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `license`
- Important functions/callbacks: `adjust_insns`, `one_switch`, `one_switch_non_zero_sec_off`, `simple_test_other_sec`, `two_switches`, `big_jump_table`, `one_jump_two_maps`, `one_map_two_jumps`, `f0`, `__static_global`, `use_static_global1`, `use_static_global2`, `use_static_global_other_sec`, `__nonstatic_global`, `use_nonstatic_global1`, `use_nonstatic_global2`, `use_nonstatic_global_other_sec`, `load_with_nonzero_offset`
- BPF helpers/kfunc-like calls: `bpf_get_current_pid_tgid`, `bpf_jiffies64`
- Mutable globals/test result fields: `in_user`, `ret_user`, `pid`, `skip`, `some_var`

## Control Flow and Data Flow

Syscall-entry programs choose branches through switches, labels, static/non-static globals, and computed jump-table-like control flow. The output is held in data globals for userspace verifier/JIT assertions.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `in_user`, `ret_user`, `pid`, `skip`, `some_var`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_current_pid_tgid`, `bpf_jiffies64`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `in_user`, `ret_user`, `pid`, `skip`, `some_var` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_gotox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_full_update_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_full_update_bench.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`
- Maps: `hash_map_bench`
- Important functions/callbacks: `loop_update_callback`, `benchmark`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_ktime_get_ns`, `bpf_loop`, `bpf_map_update_elem`
- Mutable globals/test result fields: `nr_loops`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hash_map_bench` Globals are used as userspace-visible configuration/results: `nr_loops`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_ktime_get_ns`, `bpf_loop`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nr_loops` to confirm the exercised path ran. Map contents/counts for `hash_map_bench` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_full_update_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_lookup.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`
- Maps: `hash_map_bench`
- Important functions/callbacks: `patch_key`, `lookup_callback`, `loop_lookup_callback`, `benchmark`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_ktime_get_ns`, `bpf_loop`, `bpf_map_lookup_elem`
- Mutable globals/test result fields: `nr_entries`, `nr_loops`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hash_map_bench` Globals are used as userspace-visible configuration/results: `nr_entries`, `nr_loops`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_ktime_get_ns`, `bpf_loop`, `bpf_map_lookup_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nr_entries`, `nr_loops` to confirm the exercised path ran. Map contents/counts for `hash_map_bench` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_array_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_array_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `iter/bpf_map_elem`
- Maps: `arraymap1`, `hashmap1`
- Important functions/callbacks: `dump_bpf_array_map`
- BPF helpers/kfunc-like calls: `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_seq_write`
- Mutable globals/test result fields: `key_sum`, `val_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `arraymap1`, `hashmap1` Globals are used as userspace-visible configuration/results: `key_sum`, `val_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `key_sum`, `val_sum` to confirm the exercised path ran. Map contents/counts for `arraymap1`, `hashmap1` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_array_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_hash_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_hash_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `.maps`, `iter/bpf_map_elem`, `iter.s/bpf_map_elem`
- Maps: `hashmap1`, `hashmap2`, `hashmap3`
- Important functions/callbacks: `dump_bpf_hash_map`, `sleepable_dummy_dump`
- BPF helpers/kfunc-like calls: `bpf_map_delete_elem`, `bpf_map_update_elem`
- Mutable globals/test result fields: `in_test_mode`, `key_sum_a`, `val_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hashmap1`, `hashmap2`, `hashmap3` Globals are used as userspace-visible configuration/results: `in_test_mode`, `key_sum_a`, `val_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_map_delete_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `in_test_mode`, `key_sum_a`, `val_sum` to confirm the exercised path ran. Map contents/counts for `hashmap1`, `hashmap2`, `hashmap3` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_hash_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_link.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/bpf_link`
- Important functions/callbacks: `dump_bpf_link`
- BPF helpers/kfunc-like calls: `bpf_seq_write`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/bpf_map`
- Important functions/callbacks: `dump_bpf_map`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_array_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_array_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_map_elem`
- Maps: `arraymap1`
- Important functions/callbacks: `dump_bpf_percpu_array_map`
- Mutable globals/test result fields: `key_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `arraymap1` Globals are used as userspace-visible configuration/results: `key_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `key_sum` to confirm the exercised path ran. Map contents/counts for `arraymap1` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_array_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_hash_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_hash_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_map_elem`
- Maps: `hashmap1`
- Important functions/callbacks: `dump_bpf_percpu_hash_map`
- Mutable globals/test result fields: `key_sum_a`, `val_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hashmap1` Globals are used as userspace-visible configuration/results: `key_sum_a`, `val_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `key_sum_a`, `val_sum` to confirm the exercised path ran. Map contents/counts for `hashmap1` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_hash_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_helpers.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_sk_storage_map`, `iter/task_file`, `iter/tcp`
- Maps: `sk_stg_map`
- Important functions/callbacks: `delete_bpf_sk_storage_map`, `fill_socket_owner`, `negate_socket_local_storage`
- BPF helpers/kfunc-like calls: `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_sock_from_file`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sk_stg_map`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_sock_from_file`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `sk_stg_map` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_sk_storage_map`, `iter/bpf_sk_storage_map`
- Maps: `sk_stg_map`
- Important functions/callbacks: `rw_bpf_sk_storage_map`, `oob_write_bpf_sk_storage_map`
- Mutable globals/test result fields: `val_sum`, `ipv6_sk_count`, `to_add_val`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sk_stg_map` Globals are used as userspace-visible configuration/results: `val_sum`, `ipv6_sk_count`, `to_add_val`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `val_sum`, `ipv6_sk_count`, `to_add_val` to confirm the exercised path ran. Map contents/counts for `sk_stg_map` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ipv6_route.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ipv6_route.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/ipv6_route`
- Important functions/callbacks: `dump_ipv6_route`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ipv6_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ksym.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ksym.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/ksym`
- Important functions/callbacks: `dump_ksym`
- Mutable globals/test result fields: `last_sym_value`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `last_sym_value`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `last_sym_value` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ksym.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_map_elem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_map_elem.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/bpf_map_elem`
- Important functions/callbacks: `dump_bpf_map_values`
- BPF helpers/kfunc-like calls: `bpf_probe_read_kernel`
- Mutable globals/test result fields: `value_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `value_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_probe_read_kernel`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `value_sum` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_map_elem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_netlink.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_netlink.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/netlink`
- Important functions/callbacks: `dump_netlink`
- BPF helpers/kfunc-like calls: `bpf_probe_read_kernel`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_probe_read_kernel`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_setsockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_setsockopt.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `iter/tcp`, `license`
- Important functions/callbacks: `change_tcp_cc`
- BPF helpers/kfunc-like calls: `bpf_get_prandom_u32`, `bpf_getsockopt`, `bpf_ntohs`, `bpf_setsockopt`, `bpf_skc_to_tcp_sock`, `bpf_strncmp`, `bpf_tcp_sk`
- Mutable globals/test result fields: `dctcp_cc[TCP_CA_NAME_MAX]`, `random_retry`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `dctcp_cc[TCP_CA_NAME_MAX]`, `random_retry`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_get_prandom_u32`, `bpf_getsockopt`, `bpf_ntohs`, `bpf_setsockopt`, `bpf_skc_to_tcp_sock`, `bpf_strncmp`, `bpf_tcp_sk`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `dctcp_cc[TCP_CA_NAME_MAX]`, `random_retry` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_setsockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_setsockopt_unix.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_setsockopt_unix.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `iter/unix`, `license`
- Important functions/callbacks: `cmpname`, `change_sndbuf`
- BPF helpers/kfunc-like calls: `bpf_getsockopt`, `bpf_setsockopt`
- Mutable globals/test result fields: `sun_path[AUTOBIND_LEN]`, `sndbuf_setsockopt[NR_CASES]`, `sndbuf_getsockopt[NR_CASES]`, `sndbuf_getsockopt_expected[NR_CASES]`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `sun_path[AUTOBIND_LEN]`, `sndbuf_setsockopt[NR_CASES]`, `sndbuf_getsockopt[NR_CASES]`, `sndbuf_getsockopt_expected[NR_CASES]`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `limits.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_getsockopt`, `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `sun_path[AUTOBIND_LEN]`, `sndbuf_setsockopt[NR_CASES]`, `sndbuf_getsockopt[NR_CASES]`, `sndbuf_getsockopt_expected[NR_CASES]` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_setsockopt_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_sockmap.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `.maps`, `iter/sockmap`
- Maps: `sockmap`, `sockhash`, `dst`
- Important functions/callbacks: `copy`
- BPF helpers/kfunc-like calls: `bpf_map_delete_elem`, `bpf_map_update_elem`
- Mutable globals/test result fields: `elems`, `socks`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sockmap`, `sockhash`, `dst` Globals are used as userspace-visible configuration/results: `elems`, `socks`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `errno.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_map_delete_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `elems`, `socks` to confirm the exercised path ran. Map contents/counts for `sockmap`, `sockhash`, `dst` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_sockmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_btf.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task`
- Important functions/callbacks: `dump_task_struct`
- BPF helpers/kfunc-like calls: `bpf_core_type_id_kernel`, `bpf_seq_printf_btf`
- Mutable globals/test result fields: `tasks`, `seq_err`, `skip`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `tasks`, `seq_err`, `skip`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`, `errno.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_core_type_id_kernel`, `bpf_seq_printf_btf`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `tasks`, `seq_err`, `skip` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_file.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_file.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task_file`
- Important functions/callbacks: `dump_task_file`
- Mutable globals/test result fields: `count`, `tgid`, `last_tgid`, `unique_tgid_count`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `count`, `tgid`, `last_tgid`, `unique_tgid_count`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `count`, `tgid`, `last_tgid`, `unique_tgid_count` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_stack.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task`, `iter/task`
- Important functions/callbacks: `dump_task_stack`, `get_task_user_stacks`
- BPF helpers/kfunc-like calls: `bpf_get_task_stack`, `bpf_seq_write`
- Mutable globals/test result fields: `entries[MAX_STACK_TRACE_DEPTH]`, `num_user_stacks`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `entries[MAX_STACK_TRACE_DEPTH]`, `num_user_stacks`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_get_task_stack`, `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `entries[MAX_STACK_TRACE_DEPTH]`, `num_user_stacks` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_vmas.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_vmas.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task_vma`
- BPF helpers/kfunc-like calls: `bpf_d_path`
- Mutable globals/test result fields: `d_path_buf[D_PATH_BUF_SIZE]`, `pid`, `one_task`, `one_task_error`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `d_path_buf[D_PATH_BUF_SIZE]`, `pid`, `one_task`, `one_task_error`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_d_path`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `d_path_buf[D_PATH_BUF_SIZE]`, `pid`, `one_task`, `one_task_error` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_task_vmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tasks.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tasks.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task`, `iter.s/task`
- Important functions/callbacks: `dump_task`, `dump_task_sleepable`
- BPF helpers/kfunc-like calls: `bpf_copy_from_user_task`, `bpf_copy_from_user_task_str`, `bpf_strncmp`, `bpf_task_pt_regs`
- Mutable globals/test result fields: `num_unknown_tid`, `num_known_tid`, `num_expected_failure_copy_from_user_task`, `num_expected_failure_copy_from_user_task_str`, `num_success_copy_from_user_task`, `num_success_copy_from_user_task_str`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `num_unknown_tid`, `num_known_tid`, `num_expected_failure_copy_from_user_task`, `num_expected_failure_copy_from_user_task_str`, `num_success_copy_from_user_task`, `num_success_copy_from_user_task_str`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_copy_from_user_task`, `bpf_copy_from_user_task_str`, `bpf_strncmp`, `bpf_task_pt_regs`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `num_unknown_tid`, `num_known_tid`, `num_expected_failure_copy_from_user_task`, `num_expected_failure_copy_from_user_task_str`, `num_success_copy_from_user_task`, `num_success_copy_from_user_task_str` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tasks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp4.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/tcp`
- Important functions/callbacks: `hlist_unhashed_lockless`, `timer_pending`, `sock_i_ino`, `inet_csk_in_pingpong_mode`, `tcp_in_initial_slowstart`, `dump_tcp_sock`, `dump_tw_sock`, `dump_req_sock`, `dump_tcp4`
- BPF helpers/kfunc-like calls: `bpf_jiffies64`, `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_tcp_request_sock`, `bpf_skc_to_tcp_sock`, `bpf_skc_to_tcp_timewait_sock`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_jiffies64`, `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_tcp_request_sock`, `bpf_skc_to_tcp_sock`, `bpf_skc_to_tcp_timewait_sock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp6.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/tcp`
- Important functions/callbacks: `hlist_unhashed_lockless`, `timer_pending`, `sock_i_ino`, `inet_csk_in_pingpong_mode`, `tcp_in_initial_slowstart`, `dump_tcp6_sock`, `dump_tw_sock`, `dump_req_sock`, `dump_tcp6`
- BPF helpers/kfunc-like calls: `bpf_jiffies64`, `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_tcp6_sock`, `bpf_skc_to_tcp_request_sock`, `bpf_skc_to_tcp_timewait_sock`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_jiffies64`, `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_tcp6_sock`, `bpf_skc_to_tcp_request_sock`, `bpf_skc_to_tcp_timewait_sock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern1.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `bpf_iter_test_kern_common.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern2.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `bpf_iter_test_kern_common.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern3.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task`
- Important functions/callbacks: `dump_task`
- BPF helpers/kfunc-like calls: `bpf_seq_write`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern4.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/bpf_map`
- Important functions/callbacks: `dump_bpf_map`
- BPF helpers/kfunc-like calls: `bpf_seq_write`
- Mutable globals/test result fields: `map1_id`, `map1_accessed`, `map1_seqnum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `map1_id`, `map1_accessed`, `map1_seqnum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `map1_id`, `map1_accessed`, `map1_seqnum` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern5.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_map_elem`
- Maps: `hashmap1`
- Important functions/callbacks: `dump_bpf_hash_map`
- Mutable globals/test result fields: `key_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hashmap1` Globals are used as userspace-visible configuration/results: `key_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `key_sum` to confirm the exercised path ran. Map contents/counts for `hashmap1` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern6.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/bpf_map_elem`
- Important functions/callbacks: `dump_bpf_hash_map`
- Mutable globals/test result fields: `value_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `value_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `value_sum` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern_common.h

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task`
- Important functions/callbacks: `dump_task`
- BPF helpers/kfunc-like calls: `bpf_seq_write`
- Mutable globals/test result fields: `count`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `count`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `count` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_udp4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_udp4.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/udp`
- Important functions/callbacks: `sock_i_ino`, `dump_udp4`
- BPF helpers/kfunc-like calls: `bpf_ntohs`, `bpf_probe_read_kernel`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_ntohs`, `bpf_probe_read_kernel`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_udp4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_udp6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_udp6.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/udp`
- Important functions/callbacks: `sock_i_ino`, `dump_udp6`
- BPF helpers/kfunc-like calls: `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_udp6_sock`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_udp6_sock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_udp6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_unix.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_unix.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/unix`
- Important functions/callbacks: `sock_i_ino`, `dump_unix`
- BPF helpers/kfunc-like calls: `bpf_map_update_elem`, `bpf_probe_read_kernel`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_map_update_elem`, `bpf_probe_read_kernel`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_vma_offset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_vma_offset.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/task_vma`
- Important functions/callbacks: `get_vma_offset`
- Mutable globals/test result fields: `unique_tgid_cnt`, `last_tgid`, `pid`, `page_shift`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `unique_tgid_cnt`, `last_tgid`, `pid`, `page_shift`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `unique_tgid_cnt`, `last_tgid`, `pid`, `page_shift` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_vma_offset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`
- Maps: `map1`
- Important functions/callbacks: `callback`, `empty_callback`, `nested_callback2`, `nested_callback1`, `test_prog`, `prog_null_ctx`, `prog_invalid_flags`, `prog_nested_calls`, `callback_set_f0`, `callback_set_0f`, `prog_non_constant_callback`, `stack_check_inner_callback`, `map1_lookup_elem`, `map1_update_elem`, `stack_check_outer_callback`, `stack_check`
- BPF helpers/kfunc-like calls: `bpf_get_current_pid_tgid`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Mutable globals/test result fields: `nested_callback_nr_loops`, `stop_index`, `nr_loops`, `pid`, `callback_selector`, `nr_loops_returned`, `g_output`, `err`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `map1` Globals are used as userspace-visible configuration/results: `nested_callback_nr_loops`, `stop_index`, `nr_loops`, `pid`, `callback_selector`, `nr_loops_returned`, `g_output`, `err`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_current_pid_tgid`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nested_callback_nr_loops`, `stop_index`, `nr_loops`, `pid`, `callback_selector`, `nr_loops_returned`, `g_output`, `err` to confirm the exercised path ran. Map contents/counts for `map1` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop_bench.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`
- Important functions/callbacks: `empty_callback`, `outer_loop`, `benchmark`
- BPF helpers/kfunc-like calls: `bpf_loop`
- Mutable globals/test result fields: `nr_loops`, `hits`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `nr_loops`, `hits`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_loop`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nr_loops`, `hits` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_misc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_misc.h

## Purpose

Shared selftest macro header for verifier expectations, failure annotations, architecture/compiler guards, and convenience attributes.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Integrated through the kernel BPF selftest build and libbpf skeleton loading path.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_mod_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_mod_race.c

## Purpose

Tracing selftest for module lifetime races around BPF programs, fexit hooks, and widened race windows.

## Important APIs, Types, and Functions

- BPF sections: `fmod_ret.s/bpf_fentry_test1`, `fexit/do_init_module`, `fexit/btf_try_get_module`, `license`
- Important functions/callbacks: `check_thread_id`, `BPF_PROG`, `widen_race`, `fexit_init_module`, `fexit_module_get`
- BPF helpers/kfunc-like calls: `bpf_copy_from_user`, `bpf_get_current_task_btf`, `bpf_prog_widen_race`
- Mutable globals/test result fields: `bpf_blocking`, `res_try_get_module`

## Control Flow and Data Flow

Tracing hooks filter for the selftest thread, widen selected race windows, and record whether module lookup/release paths were reached while a BPF program remains attached.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `bpf_blocking`, `res_try_get_module`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_copy_from_user`, `bpf_get_current_task_btf`, `bpf_prog_widen_race`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `bpf_blocking`, `res_try_get_module` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_mod_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_common.h

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test.

## Test Signals

Load/attach success and verifier log expectations are primary signals. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fail__incompl_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fail__incompl_ops.c

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `bpf_qdisc_test_enqueue`, `bpf_qdisc_test_dequeue`, `bpf_qdisc_test_reset`, `bpf_qdisc_test_destroy`
- BPF helpers/kfunc-like calls: `bpf_qdisc_skb_drop`

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_experimental.h`, `bpf_qdisc_common.h`. Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test. Helper availability and license restrictions matter for `bpf_qdisc_skb_drop`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fail__incompl_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fifo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fifo.c

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops/bpf_fifo_enqueue`, `struct_ops/bpf_fifo_dequeue`, `struct_ops/bpf_fifo_init`, `struct_ops/bpf_fifo_reset`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `bpf_fifo_enqueue`, `bpf_fifo_dequeue`, `bpf_fifo_init`, `bpf_fifo_reset`, `bpf_fifo_destroy`
- BPF helpers/kfunc-like calls: `bpf_for`, `bpf_kfree_skb`, `bpf_kptr_xchg`, `bpf_list_pop_front`, `bpf_list_push_back`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_qdisc_bstats_update`, `bpf_qdisc_skb_drop`, `bpf_spin_lock`, `bpf_spin_unlock`
- Mutable globals/test result fields: `init_called`

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `init_called` Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_experimental.h`, `bpf_qdisc_common.h`. Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test. Helper availability and license restrictions matter for `bpf_for`, `bpf_kfree_skb`, `bpf_kptr_xchg`, `bpf_list_pop_front`, `bpf_list_push_back`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_qdisc_bstats_update`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `init_called` to confirm the exercised path ran. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fq.c

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- BPF sections: `.struct_ops`, `license`, `.maps`, `.maps`, `struct_ops/bpf_fq_enqueue`, `struct_ops/bpf_fq_dequeue`, `struct_ops/bpf_fq_reset`, `struct_ops/bpf_fq_init`, `struct_ops`, `.struct_ops`
- Maps: `fq_nonprio_flows`, `fq_prio_flows`
- Important functions/callbacks: `bpf_kptr_xchg_back`, `skbn_tstamp_less`, `fn_time_next_packet_less`, `fq_flows_add_head`, `fq_flows_add_tail`, `fq_flows_remove_front`, `fq_flows_is_empty`, `fq_flow_set_detached`, `fq_flow_is_detached`, `sk_listener`, `fq_new_flow`, `fq_classify`, `fq_packet_beyond_horizon`, `BPF_PROG`, `fq_unset_throttled_flows`, `fq_flow_set_throttled`, `fq_check_throttled`, `fq_dequeue_nonprio_flows`, `fq_remove_flows_in_list`, `fq_gc_candidate`, `fq_remove_flows`, `fq_gc`, and 5 more
- BPF helpers/kfunc-like calls: `bpf_for`, `bpf_for_each_map_elem`, `bpf_jiffies64`, `bpf_kptr_xchg`, `bpf_kptr_xchg_back`, `bpf_ktime_get_ns`, `bpf_list_pop_front`, `bpf_list_push_back`, `bpf_list_push_front`, `bpf_loop`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_qdisc_bstats_update`, `bpf_qdisc_skb_drop`, `bpf_qdisc_watchdog_schedule`, `bpf_rbtree_add`, `bpf_rbtree_first`, `bpf_rbtree_remove`, `bpf_refcount_acquire`, and 3 more

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `fq_nonprio_flows`, `fq_prio_flows` Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Includes `vmlinux.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf_experimental.h`, `bpf_qdisc_common.h`. Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test. Helper availability and license restrictions matter for `bpf_for`, `bpf_for_each_map_elem`, `bpf_jiffies64`, `bpf_kptr_xchg`, `bpf_kptr_xchg_back`, `bpf_ktime_get_ns`, `bpf_list_pop_front`, `bpf_list_push_back`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `fq_nonprio_flows`, `fq_prio_flows` provide state validation. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_smc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_smc.c

## Purpose

SMC protocol selftest that redirects eligible TCP sockets to SMC and registers BPF struct_ops handshake policy callbacks.

## Important APIs, Types, and Functions

- BPF sections: `license`, `fentry/smc_release`, `fentry/smc_switch_to_fallback`, `.maps`, `fmod_ret/update_socket_protocol`, `struct_ops`, `struct_ops`, `.struct_ops`
- Maps: `smc_policy_ip`
- Important functions/callbacks: `BPF_PROG`, `smc_check`, `bpf_smc_release`, `bpf_smc_switch_to_fallback`, `smc_run`, `bpf_smc_set_tcp_option_cond`, `bpf_smc_set_tcp_option`
- BPF helpers/kfunc-like calls: `bpf_core_field_exists`, `bpf_get_current_task_btf`, `bpf_map_lookup_elem`
- Mutable globals/test result fields: `smc_cnt`, `fallback_cnt`, `default_ip_strat_value`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `smc_policy_ip` Globals are used as userspace-visible configuration/results: `smc_cnt`, `fallback_cnt`, `default_ip_strat_value`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf_tracing_net.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_core_field_exists`, `bpf_get_current_task_btf`, `bpf_map_lookup_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `smc_cnt`, `fallback_cnt`, `default_ip_strat_value` to confirm the exercised path ran. Map contents/counts for `smc_policy_ip` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_syscall_macro.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_syscall_macro.c

## Purpose

Syscall tracing selftest for architecture-specific PT_REGS and BPF_KSYSCALL argument extraction macros.

## Important APIs, Types, and Functions

- BPF sections: `ksyscall/prctl`, `ksyscall/splice`, `license`
- Important functions/callbacks: `BPF_KPROBE`, `BPF_KSYSCALL`
- BPF helpers/kfunc-like calls: `bpf_get_current_pid_tgid`, `bpf_probe_read_kernel`
- Mutable globals/test result fields: `arg1`, `arg2`, `arg3`, `arg4_cx`, `arg4`, `arg5`, `arg1_core`, `arg2_core`, `arg3_core`, `arg4_core_cx`, `arg4_core`, `arg5_core`, `option_syscall`, `arg2_syscall`, `arg3_syscall`, `arg4_syscall`, and 8 more

## Control Flow and Data Flow

Kprobe and ksyscall programs filter on `filter_pid`, then copy raw syscall argument registers and CO-RE macro-decoded arguments into globals for comparison.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `arg1`, `arg2`, `arg3`, `arg4_cx`, `arg4`, `arg5`, `arg1_core`, `arg2_core`, `arg3_core`, `arg4_core_cx`, `arg4_core`, `arg5_core`, `option_syscall`, `arg2_syscall`, `arg3_syscall`, `arg4_syscall`, `arg5_syscall`, `filter_pid`, `splice_fd_in`, `splice_off_in`, and 4 more

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_core_read.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_current_pid_tgid`, `bpf_probe_read_kernel`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `arg1`, `arg2`, `arg3`, `arg4_cx`, `arg4`, `arg5`, `arg1_core`, `arg2_core` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_syscall_macro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tcp_nogpl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tcp_nogpl.c

## Purpose

Negative licensing fixture for TCP congestion-control struct_ops: it uses a non-GPL license to check helper/kfunc gating.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `nogpltcp_init`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance.

## Test Signals

Load/attach success and verifier log expectations are primary signals. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tcp_nogpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_test_utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_test_utils.h

## Purpose

BPF selftest support source in the kernel selftests BPF program tree.

## Important APIs, Types, and Functions

- Important functions/callbacks: `clobber_regs_stack`
- BPF helpers/kfunc-like calls: `bpf_strtoul`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_strtoul`.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_test_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tracing_net.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tracing_net.h

## Purpose

BPF selftest support source in the kernel selftests BPF program tree.

## Important APIs, Types, and Functions

- Important functions/callbacks: `before`, `tcp_in_slow_start`, `tcp_is_cwnd_limited`
- BPF helpers/kfunc-like calls: `bpf_jiffies64`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_core_read.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_jiffies64`.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tracing_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bprm_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bprm_opts.c

## Purpose

LSM selftest using task local storage to set secure-exec behavior during binary execution.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `lsm/bprm_creds_for_exec`
- Maps: `secure_exec_task_map`
- Important functions/callbacks: `BPF_PROG`, `secure_exec`
- BPF helpers/kfunc-like calls: `bpf_bprm_opts_set`, `bpf_get_current_task_btf`, `bpf_task_storage_get`

## Control Flow and Data Flow

On `bprm_creds_for_exec`, the program fetches current-task storage, and if the stored flag is set, calls `bpf_bprm_opts_set` to request secure execution.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `secure_exec_task_map`

## Dependencies and Integration Points

Includes `linux/bpf.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_bprm_opts_set`, `bpf_get_current_task_btf`, `bpf_task_storage_get`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `secure_exec_task_map` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bprm_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays.c

## Purpose

BTF CO-RE relocation fixture for `arrays` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___diff_arr_dim.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___diff_arr_dim.c

## Purpose

BTF CO-RE relocation fixture for `arrays___diff_arr_dim` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___diff_arr_dim`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___diff_arr_dim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___diff_arr_val_sz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___diff_arr_val_sz.c

## Purpose

BTF CO-RE relocation fixture for `arrays___diff_arr_val_sz` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___diff_arr_val_sz`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___diff_arr_val_sz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___equiv_zero_sz_arr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___equiv_zero_sz_arr.c

## Purpose

BTF CO-RE relocation fixture for `arrays___equiv_zero_sz_arr` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___equiv_zero_sz_arr`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___equiv_zero_sz_arr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_bad_signed_arr_elem_sz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_bad_signed_arr_elem_sz.c

## Purpose

BTF CO-RE relocation fixture for `arrays___err_bad_signed_arr_elem_sz` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___err_bad_signed_arr_elem_sz`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_bad_signed_arr_elem_sz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_bad_zero_sz_arr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_bad_zero_sz_arr.c

## Purpose

BTF CO-RE relocation fixture for `arrays___err_bad_zero_sz_arr` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___err_bad_zero_sz_arr`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_bad_zero_sz_arr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_non_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_non_array.c

## Purpose

BTF CO-RE relocation fixture for `arrays___err_non_array` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___err_non_array`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_non_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_too_shallow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_too_shallow.c

## Purpose

BTF CO-RE relocation fixture for `arrays___err_too_shallow` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___err_too_shallow`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_too_shallow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_too_small.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_too_small.c

## Purpose

BTF CO-RE relocation fixture for `arrays___err_too_small` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___err_too_small`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_too_small.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_wrong_val_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_wrong_val_type.c

## Purpose

BTF CO-RE relocation fixture for `arrays___err_wrong_val_type` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___err_wrong_val_type`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___err_wrong_val_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___fixed_arr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___fixed_arr.c

## Purpose

BTF CO-RE relocation fixture for `arrays___fixed_arr` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `arrays___fixed_arr`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_arrays___fixed_arr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields.c

## Purpose

BTF CO-RE relocation fixture for `bitfields` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `bitfields`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___bit_sz_change.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___bit_sz_change.c

## Purpose

BTF CO-RE relocation fixture for `bitfields___bit_sz_change` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `bitfields___bit_sz_change`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___bit_sz_change.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___bitfield_vs_int.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___bitfield_vs_int.c

## Purpose

BTF CO-RE relocation fixture for `bitfields___bitfield_vs_int` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `bitfields___bitfield_vs_int`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___bitfield_vs_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___err_too_big_bitfield.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___err_too_big_bitfield.c

## Purpose

BTF CO-RE relocation fixture for `bitfields___err_too_big_bitfield` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `bitfields___err_too_big_bitfield`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___err_too_big_bitfield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___just_big_enough.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___just_big_enough.c

## Purpose

BTF CO-RE relocation fixture for `bitfields___just_big_enough` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `bitfields___just_big_enough`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_bitfields___just_big_enough.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val.c

## Purpose

BTF CO-RE relocation fixture for `enum64val` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enum64val`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___diff.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___diff.c

## Purpose

BTF CO-RE relocation fixture for `enum64val___diff` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enum64val___diff`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___err_missing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___err_missing.c

## Purpose

BTF CO-RE relocation fixture for `enum64val___err_missing` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enum64val___err_missing`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___err_missing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___val3_missing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___val3_missing.c

## Purpose

BTF CO-RE relocation fixture for `enum64val___val3_missing` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enum64val___val3_missing`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enum64val___val3_missing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval.c

## Purpose

BTF CO-RE relocation fixture for `enumval` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enumval`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___diff.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___diff.c

## Purpose

BTF CO-RE relocation fixture for `enumval___diff` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enumval___diff`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___err_missing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___err_missing.c

## Purpose

BTF CO-RE relocation fixture for `enumval___err_missing` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enumval___err_missing`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___err_missing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___val3_missing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___val3_missing.c

## Purpose

BTF CO-RE relocation fixture for `enumval___val3_missing` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `enumval___val3_missing`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_enumval___val3_missing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence.c

## Purpose

BTF CO-RE relocation fixture for `existence` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `existence`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence___minimal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence___minimal.c

## Purpose

BTF CO-RE relocation fixture for `existence___minimal` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `existence___minimal`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence___minimal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence___wrong_field_defs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence___wrong_field_defs.c

## Purpose

BTF CO-RE relocation fixture for `existence___wrong_field_defs` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `existence___wrong_field_defs`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_existence___wrong_field_defs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_flavors.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_flavors.c

## Purpose

BTF CO-RE relocation fixture for `flavors` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `flavors`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_flavors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_flavors__err_wrong_name.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_flavors__err_wrong_name.c

## Purpose

BTF CO-RE relocation fixture for `flavors__err_wrong_name` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `flavors__err_wrong_name`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_flavors__err_wrong_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints.c

## Purpose

BTF CO-RE relocation fixture for `ints` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `ints`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints___bool.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints___bool.c

## Purpose

BTF CO-RE relocation fixture for `ints___bool` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `ints___bool`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints___bool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints___reverse_sign.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints___reverse_sign.c

## Purpose

BTF CO-RE relocation fixture for `ints___reverse_sign` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `ints___reverse_sign`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ints___reverse_sign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_misc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_misc.c

## Purpose

BTF CO-RE relocation fixture for `misc` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f1`, `f2`, `f3`
- Fixture type: `misc`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods.c

## Purpose

BTF CO-RE relocation fixture for `mods` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `mods`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___mod_swap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___mod_swap.c

## Purpose

BTF CO-RE relocation fixture for `mods___mod_swap` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `mods___mod_swap`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___mod_swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___typedefs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___typedefs.c

## Purpose

BTF CO-RE relocation fixture for `mods___typedefs` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `mods___typedefs`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___typedefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting.c

## Purpose

BTF CO-RE relocation fixture for `nesting` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___anon_embed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___anon_embed.c

## Purpose

BTF CO-RE relocation fixture for `nesting___anon_embed` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___anon_embed`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___anon_embed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___dup_compat_types.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___dup_compat_types.c

## Purpose

BTF CO-RE relocation fixture for `nesting___dup_compat_types` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f1`, `f2`, `f3`
- Fixture type: `nesting___dup_compat_types`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___dup_compat_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_array_container.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_array_container.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_array_container` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___err_array_container`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_array_container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_array_field.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_array_field.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_array_field` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___err_array_field`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_array_field.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_dup_incompat_types.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_dup_incompat_types.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_dup_incompat_types` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f1`, `f2`
- Fixture type: `nesting___err_dup_incompat_types`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_dup_incompat_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_missing_container.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_missing_container.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_missing_container` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___err_missing_container`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_missing_container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_missing_field.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_missing_field.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_missing_field` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___err_missing_field`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_missing_field.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_nonstruct_container.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_nonstruct_container.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_nonstruct_container` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___err_nonstruct_container`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_nonstruct_container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_partial_match_dups.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_partial_match_dups.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_partial_match_dups` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f1`, `f2`
- Fixture type: `nesting___err_partial_match_dups`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_partial_match_dups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_too_deep.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_too_deep.c

## Purpose

BTF CO-RE relocation fixture for `nesting___err_too_deep` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___err_too_deep`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___err_too_deep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___extra_nesting.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___extra_nesting.c

## Purpose

BTF CO-RE relocation fixture for `nesting___extra_nesting` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___extra_nesting`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___extra_nesting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___struct_union_mixup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___struct_union_mixup.c

## Purpose

BTF CO-RE relocation fixture for `nesting___struct_union_mixup` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `nesting___struct_union_mixup`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_nesting___struct_union_mixup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives.c

## Purpose

BTF CO-RE relocation fixture for `primitives` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_enum_def.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_enum_def.c

## Purpose

BTF CO-RE relocation fixture for `primitives___diff_enum_def` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives___diff_enum_def`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_enum_def.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_func_proto.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_func_proto.c

## Purpose

BTF CO-RE relocation fixture for `primitives___diff_func_proto` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives___diff_func_proto`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_func_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_ptr_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_ptr_type.c

## Purpose

BTF CO-RE relocation fixture for `primitives___diff_ptr_type` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives___diff_ptr_type`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___diff_ptr_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_enum.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_enum.c

## Purpose

BTF CO-RE relocation fixture for `primitives___err_non_enum` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives___err_non_enum`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_int.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_int.c

## Purpose

BTF CO-RE relocation fixture for `primitives___err_non_int` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives___err_non_int`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_ptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_ptr.c

## Purpose

BTF CO-RE relocation fixture for `primitives___err_non_ptr` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `primitives___err_non_ptr`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_primitives___err_non_ptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ptr_as_arr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ptr_as_arr.c

## Purpose

BTF CO-RE relocation fixture for `ptr_as_arr` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `ptr_as_arr`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ptr_as_arr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ptr_as_arr___diff_sz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ptr_as_arr___diff_sz.c

## Purpose

BTF CO-RE relocation fixture for `ptr_as_arr___diff_sz` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `ptr_as_arr___diff_sz`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_ptr_as_arr___diff_sz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size.c

## Purpose

BTF CO-RE relocation fixture for `size` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `size`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___diff_offs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___diff_offs.c

## Purpose

BTF CO-RE relocation fixture for `size___diff_offs` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `size___diff_offs`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___diff_offs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___diff_sz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___diff_sz.c

## Purpose

BTF CO-RE relocation fixture for `size___diff_sz` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `size___diff_sz`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___diff_sz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___err_ambiguous.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___err_ambiguous.c

## Purpose

BTF CO-RE relocation fixture for `size___err_ambiguous` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `size___err_ambiguous`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_size___err_ambiguous.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based.c

## Purpose

BTF CO-RE relocation fixture for `type_based` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_based`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___all_missing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___all_missing.c

## Purpose

BTF CO-RE relocation fixture for `type_based___all_missing` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_based___all_missing`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___all_missing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___diff.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___diff.c

## Purpose

BTF CO-RE relocation fixture for `type_based___diff` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_based___diff`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___diff_sz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___diff_sz.c

## Purpose

BTF CO-RE relocation fixture for `type_based___diff_sz` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_based___diff_sz`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___diff_sz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___fn_wrong_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___fn_wrong_args.c

## Purpose

BTF CO-RE relocation fixture for `type_based___fn_wrong_args` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_based___fn_wrong_args`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___fn_wrong_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___incompat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___incompat.c

## Purpose

BTF CO-RE relocation fixture for `type_based___incompat` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_based___incompat`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_based___incompat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_id.c

## Purpose

BTF CO-RE relocation fixture for `type_id` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_id`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_id___missing_targets.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_id___missing_targets.c

## Purpose

BTF CO-RE relocation fixture for `type_id___missing_targets` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `type_id___missing_targets`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case. Negative variants with `err_` or `missing` in the name intentionally expect relocation failure or missing-target behavior.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_type_id___missing_targets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_data.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- Important functions/callbacks: `func`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_bitfields.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_bitfields.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `stdbool.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_bitfields.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_multidim.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_multidim.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_multidim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_namespacing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_namespacing.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_namespacing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_ordering.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_ordering.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_ordering.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_packing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_packing.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_packing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_padding.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_padding.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_padding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_syntax.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_syntax.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_dump_test_case_syntax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_ptr.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_ptr.h

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `vmlinux.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Risk is expected-output drift from compiler, pahole, or BTF dumper formatting changes. Padding, packing, bitfield, namespace, and syntax fixtures are sensitive to ABI and C frontend details.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_ptr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- BPF sections: `fentry/bpf_fentry_test1`
- Important functions/callbacks: `BPF_PROG`, `sub`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_percpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_percpu.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- BPF sections: `fentry/bpf_testmod_test_btf_type_tag_percpu_1`, `fentry/bpf_testmod_test_btf_type_tag_percpu_2`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `license`
- Important functions/callbacks: `BPF_PROG`, `test_percpu1`, `test_percpu2`, `test_percpu_load`, `test_percpu_helper`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`
- Mutable globals/test result fields: `g`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g` to confirm the exercised path ran. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_percpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_user.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- BPF sections: `fentry/bpf_testmod_test_btf_type_tag_user_1`, `fentry/bpf_testmod_test_btf_type_tag_user_2`, `fentry/__sys_getsockname`
- Important functions/callbacks: `BPF_PROG`, `test_user1`, `test_user2`, `test_sys_getsockname`
- Mutable globals/test result fields: `g`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g` to confirm the exercised path ran. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cb_refs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cb_refs.c

## Purpose

Reference tracking verifier fixture that moves acquired kfunc references through callback paths to test leak/underflow detection.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `?tc`, `?tc`, `?tc`, `?tc`, `license`
- Maps: `array_map`
- Important functions/callbacks: `cb1`, `underflow_prog`, `cb2`, `leak_prog`, `cb`, `cb3`, `nested_cb`, `non_cb_transfer_ref`
- BPF helpers/kfunc-like calls: `bpf_for_each_map_elem`, `bpf_kfunc_call_test_acquire`, `bpf_kfunc_call_test_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `array_map`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `../test_kmods/bpf_testmod_kfunc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_for_each_map_elem`, `bpf_kfunc_call_test_acquire`, `bpf_kfunc_call_test_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `array_map` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cb_refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi.h

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_egress_only.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_egress_only.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `cgroup_skb/egress`
- Maps: `cgroup_storage`
- Important functions/callbacks: `egress`
- BPF helpers/kfunc-like calls: `bpf_get_local_storage`
- Mutable globals/test result fields: `invocations`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `cgroup_storage` Globals are used as userspace-visible configuration/results: `invocations` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `linux/ip.h`, `linux/udp.h`, `bpf/bpf_helpers.h`, `progs/cg_storage_multi.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_local_storage`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `invocations` to confirm the exercised path ran. Map contents/counts for `cgroup_storage` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_egress_only.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_isolated.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_isolated.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `cgroup_skb/egress`, `cgroup_skb/egress`, `cgroup_skb/ingress`
- Maps: `cgroup_storage`
- Important functions/callbacks: `egress1`, `egress2`, `ingress`
- BPF helpers/kfunc-like calls: `bpf_get_local_storage`
- Mutable globals/test result fields: `invocations`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `cgroup_storage` Globals are used as userspace-visible configuration/results: `invocations` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `linux/ip.h`, `linux/udp.h`, `bpf/bpf_helpers.h`, `progs/cg_storage_multi.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_local_storage`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `invocations` to confirm the exercised path ran. Map contents/counts for `cgroup_storage` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_isolated.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_shared.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_shared.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `cgroup_skb/egress`, `cgroup_skb/egress`, `cgroup_skb/ingress`
- Maps: `cgroup_storage`
- Important functions/callbacks: `egress1`, `egress2`, `ingress`
- BPF helpers/kfunc-like calls: `bpf_get_local_storage`
- Mutable globals/test result fields: `invocations`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `cgroup_storage` Globals are used as userspace-visible configuration/results: `invocations` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `linux/ip.h`, `linux/udp.h`, `bpf/bpf_helpers.h`, `progs/cg_storage_multi.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_local_storage`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `invocations` to confirm the exercised path ran. Map contents/counts for `cgroup_storage` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_ancestor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_ancestor.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `tc`, `license`
- Important functions/callbacks: `log_nth_level`, `log_cgroup_id`
- BPF helpers/kfunc-like calls: `bpf_core_cast`, `bpf_skb_ancestor_cgroup_id`
- Mutable globals/test result fields: `cgroup_ids[NUM_CGROUP_LEVELS]`, `dport`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `cgroup_ids[NUM_CGROUP_LEVELS]`, `dport` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`, `bpf_tracing_net.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_core_cast`, `bpf_skb_ancestor_cgroup_id`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `cgroup_ids[NUM_CGROUP_LEVELS]`, `dport` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_ancestor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_getsockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_getsockopt.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`
- Important functions/callbacks: `get_retval`, `set_eisconn`, `clear_retval`
- BPF helpers/kfunc-like calls: `bpf_get_retval`, `bpf_set_retval`
- Mutable globals/test result fields: `invocations`, `assertion_error`, `retval_value`, `ctx_retval_value`, `page_size`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `invocations`, `assertion_error`, `retval_value`, `ctx_retval_value`, `page_size` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_retval`, `bpf_set_retval`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `invocations`, `assertion_error`, `retval_value`, `ctx_retval_value`, `page_size` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_getsockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_hooks.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_hooks.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF helpers/kfunc-like calls: `bpf_get_retval`, `bpf_set_retval`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_helpers.h`, `cgroup_getset_retval_hooks.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_retval`, `bpf_set_retval`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_setsockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_setsockopt.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/setsockopt`, `cgroup/setsockopt`, `cgroup/setsockopt`, `cgroup/setsockopt`
- Important functions/callbacks: `get_retval`, `set_eunatch`, `set_eisconn`, `legacy_eperm`
- BPF helpers/kfunc-like calls: `bpf_get_retval`, `bpf_set_retval`
- Mutable globals/test result fields: `invocations`, `assertion_error`, `retval_value`, `page_size`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `invocations`, `assertion_error`, `retval_value`, `page_size` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_retval`, `bpf_set_retval`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `invocations`, `assertion_error`, `retval_value`, `page_size` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_getset_retval_setsockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_hierarchical_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_hierarchical_stats.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `tp_btf/cgroup_attach_task`, `fentry/bpf_rstat_flush`, `iter.s/cgroup`
- Maps: `percpu_attach_counters`, `attach_counters`
- Important functions/callbacks: `create_percpu_attach_counter`, `create_attach_counter`, `BPF_PROG`, `counter`, `flusher`, `dumper`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_map_lookup_percpu_elem`, `bpf_map_update_elem`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `percpu_attach_counters`, `attach_counters` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_map_lookup_percpu_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `percpu_attach_counters`, `attach_counters` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_hierarchical_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/cgroup`
- Important functions/callbacks: `cgroup_id`, `cgroup_id_printer`
- Mutable globals/test result fields: `terminate_early`, `terminal_cgroup`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `terminate_early`, `terminal_cgroup` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `terminate_early`, `terminal_cgroup` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter_memcg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter_memcg.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.data.query`, `iter.s/cgroup`
- Important functions/callbacks: `cgroup_memcg_query`
- BPF helpers/kfunc-like calls: `bpf_core_enum_value`, `bpf_get_mem_cgroup`, `bpf_mem_cgroup_flush_stats`, `bpf_mem_cgroup_page_state`, `bpf_mem_cgroup_vm_events`, `bpf_put_mem_cgroup`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_core_read.h`, `cgroup_iter_memcg.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_core_enum_value`, `bpf_get_mem_cgroup`, `bpf_mem_cgroup_flush_stats`, `bpf_mem_cgroup_page_state`, `bpf_mem_cgroup_vm_events`, `bpf_put_mem_cgroup`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter_memcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_mprog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_mprog.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`
- Important functions/callbacks: `getsockopt_1`, `getsockopt_2`, `getsockopt_3`, `getsockopt_4`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_mprog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_preorder.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_preorder.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`
- Important functions/callbacks: `child`, `child_2`, `parent`, `parent_2`
- Mutable globals/test result fields: `result[4]`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `result[4]` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `result[4]` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_preorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_read_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_read_xattr.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `lsm.s/socket_connect`, `lsm/socket_connect`, `lsm/socket_connect`, `lsm.s/socket_connect`, `lsm.s/socket_connect`, `lsm/socket_connect`, `cgroup/sendmsg4`
- Important functions/callbacks: `read_xattr`, `BPF_PROG`, `trusted_cgroup_ptr_sleepable`, `trusted_cgroup_ptr_non_sleepable`, `use_css_iter_non_sleepable`, `use_css_iter_sleepable_missing_rcu_lock`, `use_css_iter_sleepable_with_rcu_lock`, `use_bpf_cgroup_ancestor`, `cgroup_skb`
- BPF helpers/kfunc-like calls: `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_read_xattr`, `bpf_cgroup_release`, `bpf_dynptr_from_mem`, `bpf_for_each`, `bpf_get_current_cgroup_id`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`
- Mutable globals/test result fields: `value[16]`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `value[16]` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`, `bpf_experimental.h`, `bpf_misc.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_read_xattr`, `bpf_cgroup_release`, `bpf_dynptr_from_mem`, `bpf_for_each`, `bpf_get_current_cgroup_id`, `bpf_rcu_read_lock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `value[16]` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_read_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_direct_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_direct_packet_access.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `cgroup_skb/ingress`, `license`
- Important functions/callbacks: `direct_packet_access`
- Mutable globals/test result fields: `data_end`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `data_end` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `data_end` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_direct_packet_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_sk_lookup_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_sk_lookup_kern.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup_skb/ingress`
- Important functions/callbacks: `set_ip`, `set_tuple`, `is_allowed_peer_cg`, `ingress_lookup`
- BPF helpers/kfunc-like calls: `bpf_htons`, `bpf_sk_ancestor_cgroup_id`, `bpf_sk_cgroup_id`, `bpf_sk_lookup_tcp`, `bpf_sk_release`, `bpf_skb_ancestor_cgroup_id`, `bpf_skb_cgroup_id`, `bpf_skb_load_bytes`
- Mutable globals/test result fields: `g_serv_port`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g_serv_port` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`, `linux/if_ether.h`, `linux/in.h`, `linux/in6.h`, `linux/ipv6.h`, `linux/tcp.h`, `sys/types.h`, `sys/socket.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_htons`, `bpf_sk_ancestor_cgroup_id`, `bpf_sk_cgroup_id`, `bpf_sk_lookup_tcp`, `bpf_sk_release`, `bpf_skb_ancestor_cgroup_id`, `bpf_skb_cgroup_id`, `bpf_skb_load_bytes`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g_serv_port` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_sk_lookup_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_storage.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `cgroup_skb/egress`, `.maps`, `.maps`, `cgroup/sock_create`, `license`
- Maps: `cgroup_storage`, `cgroup_storage_oob`, `lru_map`
- Important functions/callbacks: `bpf_prog`, `trigger_oob`
- BPF helpers/kfunc-like calls: `bpf_get_local_storage`, `bpf_long_memcpy`, `bpf_map_update_elem`, `bpf_obj_memcpy`, `bpf_prog`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `cgroup_storage`, `cgroup_storage_oob`, `lru_map` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_local_storage`, `bpf_long_memcpy`, `bpf_map_update_elem`, `bpf_obj_memcpy`, `bpf_prog`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `cgroup_storage`, `cgroup_storage_oob`, `lru_map` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_tcp_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_tcp_skb.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup_skb/egress`, `cgroup_skb/ingress`, `cgroup_skb/egress`, `cgroup_skb/ingress`, `cgroup_skb/egress`, `cgroup_skb/ingress`, `cgroup_skb/egress`, `cgroup_skb/ingress`
- Important functions/callbacks: `needed_tcp_pkt`, `egress_accept`, `ingress_accept`, `egress_connect`, `ingress_connect`, `egress_close_remote`, `ingress_close_remote`, `egress_close_local`, `ingress_close_local`, `server_egress`, `server_ingress`, `server_egress_srv`, `server_ingress_srv`, `client_egress_srv`, `client_ingress_srv`, `client_egress`, `client_ingress`
- BPF helpers/kfunc-like calls: `bpf_htons`, `bpf_skb_load_bytes`
- Mutable globals/test result fields: `g_sock_port`, `g_sock_state`, `g_unexpected`, `g_packet_count`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g_sock_port`, `g_sock_state`, `g_unexpected`, `g_packet_count` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`, `linux/if_ether.h`, `linux/in.h`, `linux/in6.h`, `linux/ipv6.h`, `linux/tcp.h`, `sys/types.h`, `sys/socket.h`, `cgroup_tcp_skb.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_htons`, `bpf_skb_load_bytes`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g_sock_port`, `g_sock_state`, `g_unexpected`, `g_packet_count` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_tcp_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_common.h

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`
- Maps: `__cgrps_kfunc_map`
- Important functions/callbacks: `cgrps_kfunc_map_insert`
- BPF helpers/kfunc-like calls: `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `__cgrps_kfunc_map` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `__cgrps_kfunc_map` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_failure.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `kretprobe/cgroup_destroy_locked`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`
- Important functions/callbacks: `BPF_PROG`, `cgrp_kfunc_acquire_untrusted`, `cgrp_kfunc_acquire_no_null_check`, `cgrp_kfunc_acquire_fp`, `cgrp_kfunc_acquire_unsafe_kretprobe`, `cgrp_kfunc_acquire_trusted_walked`, `cgrp_kfunc_acquire_null`, `cgrp_kfunc_acquire_unreleased`, `cgrp_kfunc_xchg_unreleased`, `cgrp_kfunc_rcu_get_release`, `cgrp_kfunc_release_untrusted`, `cgrp_kfunc_release_fp`, `cgrp_kfunc_release_null`, `cgrp_kfunc_release_unacquired`
- BPF helpers/kfunc-like calls: `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`, `cgrp_kfunc_common.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_success.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `syscall`
- Important functions/callbacks: `is_test_kfunc_task`, `BPF_PROG`, `test_cgrp_from_id_ns`, `test_cgrp_acquire_release_argument`, `test_cgrp_acquire_leave_in_map`, `test_cgrp_xchg_release`, `test_cgrp_get_release`, `test_cgrp_get_ancestors`, `test_cgrp_from_id`
- BPF helpers/kfunc-like calls: `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_get_current_pid_tgid`, `bpf_kptr_xchg`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `cgrp_kfunc_common.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_get_current_pid_tgid`, `bpf_kptr_xchg`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_attach_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_attach_cgroup.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `cgroup/connect6`, `sockops`, `fexit/inet_stream_connect`
- Maps: `socket_cookies`
- Important functions/callbacks: `set_cookie`, `update_cookie_sockops`, `BPF_PROG`, `update_cookie_tracing`
- BPF helpers/kfunc-like calls: `bpf_cgrp_storage_get`, `bpf_get_socket_cookie`, `bpf_skc_to_tcp_sock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `socket_cookies` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf_tracing_net.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgrp_storage_get`, `bpf_get_socket_cookie`, `bpf_skc_to_tcp_sock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `socket_cookies` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_attach_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_negative.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_negative.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `tp_btf/sys_enter`
- Maps: `map_a`
- Important functions/callbacks: `BPF_PROG`, `on_enter`
- BPF helpers/kfunc-like calls: `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `map_a` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `map_a` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_negative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_recursion.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `fentry/bpf_local_storage_update`, `tp_btf/sys_enter`
- Maps: `map_a`, `map_b`
- Important functions/callbacks: `__on_update`, `BPF_PROG`, `__on_enter`, `on_update`, `on_enter`
- BPF helpers/kfunc-like calls: `bpf_cgroup_release`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_task_get_cgroup1`
- Mutable globals/test result fields: `target_hid`, `is_cgroup1`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `map_a`, `map_b` Globals are used as userspace-visible configuration/results: `target_hid`, `is_cgroup1` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_release`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_task_get_cgroup1`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `target_hid`, `is_cgroup1` to confirm the exercised path ran. Map contents/counts for `map_a`, `map_b` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_recursion.c -->
