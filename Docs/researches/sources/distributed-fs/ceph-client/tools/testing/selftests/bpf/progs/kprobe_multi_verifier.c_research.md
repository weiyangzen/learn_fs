<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_verifier.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_verifier.c

Purpose: Verifier return-value range tests for kprobe.session programs, including valid 0/1 and invalid 2 return values. The file has 32 source lines and 582 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.session:kprobe_session_return_0, kprobe.session:kprobe_session_return_1, kprobe.session:kprobe_session_return_2`. Local functions/subprograms: `kprobe_session_return_0, kprobe_session_return_1, kprobe_session_return_2`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `At program exit the register R0 has smin=2 smax=2 should have been in [0, 1]`.

Control flow: Entry points are BPF programs in `kprobe.session:kprobe_session_return_0, kprobe.session:kprobe_session_return_1, kprobe.session:kprobe_session_return_2`. Control flow is centered on annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `At program exit the register R0 has smin=2 smax=2 should have been in [0, 1]`; successful attachment/execution of kprobe.session:kprobe_session_return_0, kprobe.session:kprobe_session_return_1, kprobe.session:kprobe_session_return_2; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_verifier.c -->
