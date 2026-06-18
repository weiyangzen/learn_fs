# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trampoline_count.c

## Purpose
Tests enforcement of the kernel maximum number of BPF trampoline links for fentry/fmod_ret/fexit programs.

## APIs, Types, and Functions
Defines `struct inst`, `load_prog()`, and `test_trampoline_count()`. Uses `get_bpf_max_tramp_links()` and `trigger_module_test_read()`.

## Control Flow, State, and Persistence
The test allocates one more instance slot than the kernel limit. It repeatedly opens, loads, finds, and attaches programs from `test_trampoline_count.bpf.o` up to the limit. It then loads one extra fmod_ret program and asserts attach fails with `-E2BIG` and a null link pointer. Finally it triggers the probed module function and destroys all links/objects.

## Dependencies and Integration
Depends on libbpf object APIs, BPF test module trigger, and kernel trampoline accounting.

## Risks and Test Signals
Risks include leaks on partial load failure, module trigger availability, and limit semantics changing. Signals are successful attaches up to the reported limit, `-E2BIG` for the extra attach, and successful module trigger after attachments.
