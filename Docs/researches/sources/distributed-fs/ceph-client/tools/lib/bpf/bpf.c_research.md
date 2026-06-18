<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.c

## Purpose
`bpf.c` is libbpf's low-level wrapper around the Linux `bpf(2)` syscall. It converts stable C APIs and option structs into correctly sized `union bpf_attr` payloads, handles fd sanitization, maps errno into libbpf return conventions, and provides compatibility retries for selected kernel-version differences.

## Important APIs, types, and functions
Foundational helpers are `ptr_to_u64()`, `sys_bpf()`, `sys_bpf_fd()`, and `sys_bpf_prog_load()`. Public APIs include map creation and operations, program load/query/test-run/attach/detach, BPF link create/update/detach, object pin/get, ID iteration and fd-by-id lookup, info-by-fd wrappers, raw tracepoint open, BTF load, task fd query, stats enable, program-map binding, BPF token creation, stream read, and struct_ops association. `probe_memcg_account()`, `libbpf_set_memlock_rlim()`, and `bump_rlimit_memlock()` manage old memlock accounting behavior.

## Control flow
Each wrapper validates option struct size with `OPTS_VALID()`, zeroes only the supported attr prefix with `offsetofend()`, fills command-specific fields, calls `sys_bpf()`, and returns either fd or negative errno through libbpf helpers. Program and BTF load optionally retry with verifier logs. `bpf_prog_load()` also retries after kernel-reported func/line info record-size differences by allocating zero-tailed compatibility records. `bpf_link_create()` falls back to `BPF_RAW_TRACEPOINT_OPEN` for old kernels and eligible tracing attach types.

## State and persistence behavior
Global state is limited to memlock auto-bump controls: `memlock_bumped` and `memlock_rlim`. Kernel-created maps, programs, links, BTF objects, tokens, and pinned objects persist by fd or bpffs lifetime according to kernel rules, not by this file.

## Dependencies and integration points
It depends on Linux UAPI `linux/bpf.h`, syscall numbers per architecture, libbpf internal option and error helpers, feature probing, fd hygiene, and kernel support for each BPF command. Higher-level libbpf object loading code uses these wrappers as its syscall boundary.

## Risks and edge cases
Attr sizing must track UAPI evolution exactly; too-small sizes omit features, too-large sizes can fail on older kernels. Global memlock bumping is process-wide and not thread-isolated. Many APIs require mutually exclusive option fields; validation mistakes can send ambiguous attrs. Compatibility retry code must preserve errno and caller log buffers carefully.

## Test signals
Run libbpf selftests across old/new kernels and privilege modes. Specific coverage should include map CRUD and batch ops, program load with and without logs, BTF load retry, link-create fallback, fd-by-id/info queries, memcg versus memlock accounting, token fd fields, and invalid option sizes/field combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.c -->
