# sources/distributed-fs/ceph-client/samples/seccomp/bpf-fancy.c

## Purpose

This user-space sample builds a seccomp filter with label and comparison macros from `bpf-helper.h`, demonstrating readable construction of nontrivial BPF policy.

## Important APIs, Types, and Functions

It uses `struct bpf_labels`, macros `LOAD_SYSCALL_NR`, `SYSCALL`, `LABEL`, `JUMP`, `ARG`, `JEQ/JNE/JGE/JLT`, `ALLOW`, `DENY`, and helper `bpf_resolve_jumps()`. Runtime seccomp installation uses `prctl(PR_SET_NO_NEW_PRIVS)` and `prctl(PR_SET_SECCOMP)`.

## Control Flow

The filter allows exit syscalls, routes write and read checks through labels, permits reads only from stdin into the program's `buf` with length below the buffer, and permits writes only to stdout/stderr from known buffer addresses and bounded lengths. After installing the filter, the program prompts, reads, echoes through stderr, then intentionally writes too much from `msg2` to trigger the deny rule.

## State and Persistence Behavior

The label table is temporary setup state. The seccomp filter persists on the process after installation.

## Dependencies and Integration Points

It depends on `bpf-helper.c/h`, seccomp filter support, and stable local buffer addresses after filter installation.

## Risks and Edge Cases

The policy compares user pointer values to specific process addresses, so code changes that alter buffers must update the policy. The final over-length write is expected to kill the process.

## Test Signals

Run the program, provide input, observe allowed prompt/echo output, and verify the final write terminates the process under seccomp.
