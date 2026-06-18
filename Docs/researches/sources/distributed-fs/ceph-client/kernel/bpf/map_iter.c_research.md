# sources/distributed-fs/ceph-client/kernel/bpf/map_iter.c

Purpose: registers BPF iterator targets for iterating BPF maps and map elements, exposes fdinfo/link-info for map element iterators, and registers the `bpf_map_sum_elem_count` kfunc. The source was read as a complete 229-line file.

Important APIs/functions: `bpf_map_seq_start`, `bpf_map_seq_next`, `bpf_map_seq_show`, `bpf_map_seq_stop`, `bpf_iter_attach_map`, `bpf_iter_detach_map`, `bpf_iter_map_show_fdinfo`, `bpf_iter_map_fill_link_info`, `bpf_map_iter_init`, `bpf_map_sum_elem_count`, and the late init kfunc registration. It defines iterator contexts `struct bpf_iter__bpf_map` and uses generated `struct bpf_iter__bpf_map_elem`.

Control flow: the generic map iterator stores the current map ID in `seq->private`, gets the current or next map with a reference, runs the attached iterator BPF program in `show`, and drops refs in `next`/`stop`. The map-element iterator attach path accepts only hash, LRU hash, array, and their percpu variants, then verifies the iterator program's maximum key/value access against actual map key/value storage. Late init registers `bpf_map` and `bpf_map_elem` targets and separately registers the elem-count kfunc for all program types.

State and persistence: iterator state is per-open seq-file private data. Map refs are acquired for the current element and released as the sequence advances. Map-element links hold a user ref to the target map through `aux->map` until detach. `bpf_map_sum_elem_count` only reads per-CPU `elem_count` counters and returns zero if unavailable.

Dependencies/integration: integrates with `bpf_iter_reg_target`, BTF IDs for `struct bpf_map`, `bpf_iter_run_prog`, map registry ID iteration, map user refs, seq_file, and BTF kfunc ID registration. The preload iterator program calls the kfunc to print current element counts.

Risks and edge cases: map ID iteration races with map deletion and relies on ref acquisition helpers. Access bounds must account for percpu value expansion using `round_up(value_size, 8) * num_possible_cpus()`. `stop` runs the iterator program with a NULL map on end, so iterator programs must tolerate NULL context pointers.

Test signals: BPF iterator selftests for map iteration, map element iterator access bounds, fdinfo/link-info contents, detaching map links, percpu map values, and kfunc invocation from iterator programs.
