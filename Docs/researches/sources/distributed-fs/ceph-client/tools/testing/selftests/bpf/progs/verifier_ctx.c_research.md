# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx.c

## Purpose

`verifier_ctx.c` is a broad verifier test suite for `PTR_TO_CTX` handling. It covers direct context access, atomic stores, modified context pointers passed to helpers, nullable context parameters, field width and alignment rules, syscall context memory access, helper and kfunc memory access to ctx, and non-syscall restrictions.

## Important APIs, Types, and Functions

The file uses `vmlinux.h`, libbpf helpers, `bpf_misc.h`, and test-module kfunc declarations from `bpf_testmod_kfunc.h`. Program sections include tc, socket, cgroup sendmsg/connect/post_bind, and many optional `?syscall` programs. Helper and kfunc coverage includes `bpf_probe_read_kernel`, `bpf_snprintf`, `bpf_strncmp`, `bpf_get_prandom_u32`, and `bpf_kfunc_call_test_mem_len_pass1`. Macros generate invalid narrow-load, unaligned-field, and padding-access cases for context structs.

## Control Flow

Early tests mutate or arithmetically adjust ctx pointers and verify that direct dereference or helper passing is rejected unless the original unmodified ctx is used. The cgroup cases check helper prototypes accepting either ctx or null. The syscall section deliberately treats ctx as a generic memory region: fixed, variable, aligned, unaligned, zero-sized, helper-mediated, and kfunc-mediated access is accepted when bounded and rejected past `U16_MAX`, for negative variable offsets, or for unbounded ranges. The final macro block applies stricter rules to other program types, rejecting modified ctx dereferences and helper/kfunc access through ctx.

## State and Persistence Behavior

The file has no BPF maps. Its state is verifier state: ctx pointer id and offset, variable offset ranges, program-type-specific context access tables, helper/kfunc memory argument classification, and nullable ctx acceptance. Syscall programs are intentionally special because their ctx argument can be treated as trusted kernel memory under bounded access rules.

## Dependencies and Integration Points

The tests integrate with verifier context access callbacks for each program type, BTF-backed kfunc prototype checking, helper argument validators, and the selftest module that exports test kfuncs. Optional sections allow loaders to skip unavailable program types while still validating supported ones.

## Risks and Test Signals

Risks are accepting modified ctx pointers where helpers expect original ctx, rejecting legitimate bounded syscall ctx memory, or allowing out-of-range syscall ctx access. Test signals include exact errors for atomic ctx stores, modified ctx pointer dereference, invalid context access, negative or unbounded memory ranges, and type mismatches such as ctx where stack memory is expected.
