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
