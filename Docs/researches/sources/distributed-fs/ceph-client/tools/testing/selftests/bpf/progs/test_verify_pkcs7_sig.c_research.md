<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verify_pkcs7_sig.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verify_pkcs7_sig.c

## Purpose

Sleepable LSM test for PKCS#7 signature verification kfuncs and kernel/user key lookup. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 92 source lines. BPF sections: `.maps`, `license`, `lsm.s/bpf`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_attr`, `bpf_copy_from_user`, `bpf_dynptr`, `bpf_dynptr_from_mem`, `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_key`, `bpf_key_put`, `bpf_kfuncs`, `bpf_lookup_system_key`, `bpf_lookup_user_key`, `bpf_map_lookup_elem`, `bpf_probe_read_kernel`, `bpf_tracing`, `bpf_verify_pkcs7_signature`. Important C functions and entry points include `BPF_PROG`. Notable globals or configuration/result fields include `__u32 monitored_pid`; `__u64 system_keyring_id`; `int BPF_PROG(bpf, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)`.

## Control Flow

The LSM hook filters on `monitored_pid`, copies a `struct data` from a user pointer stored in `union bpf_attr`, creates dynptrs over payload and signature, looks up user or system keyring, verifies the signature, releases the key, and maps errors.

## State And Persistence Behavior

`data_input` stores up to 1 MiB payload plus 1 KiB signature; keyring ids and monitored pid are globals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Bounds checks before dynptr creation, key reference release, and sleepable LSM context are essential for safety. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should run valid/invalid signatures against user and system keyrings and verify returned errno. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verify_pkcs7_sig.c -->
