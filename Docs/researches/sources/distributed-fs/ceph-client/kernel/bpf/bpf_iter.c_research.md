# sources/distributed-fs/ceph-client/kernel/bpf/bpf_iter.c

Purpose: implements BPF iterator target registration, iterator link creation, iterator file operations, seq_file integration, and generic callback helpers such as `bpf_loop`.

Important APIs/types/functions: target and link types are `bpf_iter_target_info`, `bpf_iter_link`, and `bpf_iter_priv_data`. Public APIs include `bpf_iter_reg_target`, `bpf_iter_unreg_target`, `bpf_iter_prog_supported`, `bpf_iter_get_func_proto`, `bpf_iter_link_attach`, `bpf_iter_new_fd`, `bpf_iter_get_info`, and `bpf_iter_run_prog`. Helpers include `bpf_for_each_map_elem`, `bpf_loop`, and numeric iterator kfuncs `bpf_iter_num_new`, `bpf_iter_num_next`, `bpf_iter_num_destroy`.

Control flow: targets register static metadata under `targets_mutex`. Program verification checks attach function prefix and target name/BTF id, then initializes context arg info. Link attach validates user iterator info, finds target by cached BTF id, enforces sleepable/resched compatibility, primes a BPF link, and calls target attach hooks. Opening an iterator anon inode prepares a seq_file, pins the current program under `link_mutex`, initializes target-private seq state, and assigns a unique session id. Reads use custom `bpf_seq_read` to run seq start/show/next/stop with a fixed buffer, sequence numbering, overflow handling, optional rescheduling, and object-count cap.

State and persistence: registered targets persist until unregistered. Iterator links persist as BPF links and may be updated with compatible programs. Each open file has private session/sequence state and target-private data. Numeric iterators store current/end in BPF stack-visible iterator storage.

Dependencies and integration: depends on anon inodes, seq_file, BPF link core, BTF attach ids, BPF program run context, RCU trace/dont-migrate locking, map iterator seq info, and target-specific attach/detach/fdinfo callbacks.

Risks: iterator read loops must handle buggy `next` functions, overflow, skipped objects, and long scans without livelock. Link update must protect program lifetime. Sleepable programs are allowed only for resched-capable targets. User link info copying must preserve tail-zero validation.

Test signals: BPF iterator selftests for task/map/prog/link targets, link fdinfo/info, program replacement, sleepable iterator constraints, partial reads and overflow, `bpf_for_each_map_elem`, `bpf_loop`, and numeric iterator kfunc bounds.
