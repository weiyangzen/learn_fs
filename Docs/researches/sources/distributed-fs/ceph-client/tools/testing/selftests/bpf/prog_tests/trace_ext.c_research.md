# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_ext.c

## Purpose
Validates tracing a freplace extension program: a classifier program is replaced by an extension and fentry/fexit tracing programs attach to the extension.

## APIs, Types, and Functions
Entry point `test_trace_ext()` uses skeletons `test_pkt_md_access`, `test_trace_ext`, and `test_trace_ext_tracing`. It calls `bpf_program__set_attach_target()` twice: first to attach an extension to the base program, then to attach tracing programs to the extension fd.

## Control Flow, State, and Persistence
The base packet metadata program is open/load/attached. The extension skeleton is opened, its replacement program target is set to the base program fd and function name, then it loads and attaches. The tracing skeleton is opened, fentry and fexit target the extension fd/function, then it loads and attaches. A test packet run triggers the base program; BSS counters verify the extension ran and fentry/fexit counts equal extension invocations.

## Dependencies and Integration
Depends on packet data from `network_helpers`, libbpf attach-target APIs, freplace, fentry/fexit support, and the three generated skeletons.

## Risks and Test Signals
Risks include attach target name/fd mismatch, verifier changes around tracing extension programs, and BTF availability. Signals are nonzero extension call count, fentry/fexit counters equal to extension count, and successful program test run.
