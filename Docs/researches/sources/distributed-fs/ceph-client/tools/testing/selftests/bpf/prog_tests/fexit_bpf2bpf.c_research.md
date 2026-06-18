# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_bpf2bpf.c

## Purpose
Comprehensively tests tracing and extension programs attached to BPF-to-BPF functions: fexit, freplace, fmod_ret rejection, multiple replacement attachments, cgroup BPF fentry, program-map compatibility, and invalid replacement cases.

## Important APIs, types, and functions
Uses many external `.bpf.o` files plus skeletons `bind4_prog`, `freplace_progmap`, and `xdp_dummy`. `test_fexit_bpf2bpf_common()` loads target object, gets target program ID/BTF, sets attach targets for all programs in the tracing/replacement object, loads, attaches traces, validates `bpf_link_info` target object/BTF IDs, optionally runs target with `bpf_prog_test_run_opts()`, and checks internal data map. Helpers cover second attach, load-failure log assertions, manual fentry load with `attach_prog_fd`/`attach_btf_id`, and cpumap owner compatibility.

## Control flow and state
`serial_test_fexit_bpf2bpf()` runs many subtests serially because they can affect other tests. Runtime state includes target/tracing BPF objects, arrays of programs/links, target program IDs/BTF IDs, internal data maps, cgroup FD for cgroup BPF fentry, and cpumap update state. Cleanup destroys links and closes all objects per subtest.

## Dependencies and integration points
Depends on BPF trampoline, fexit/fentry/freplace, BTF function metadata, cgroup BPF attach, XDP/cpumap maps, verifier diagnostics, and numerous generated target objects. It is a central integration test for tracing/ext programs.

## Risks and test signals
Risks include global serial side effects, verifier log wording, BTF ID lookup failures, and target object mismatch. Passing signals are correct link attach metadata, internal result map entries set to one, expected load failures for invalid replacements, successful cgroup-BPF fentry info fields, and successful cpumap update through freplace target resolution.
