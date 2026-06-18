# sources/distributed-fs/ceph-client/tools/include/linux/filter.h

## Purpose

This header provides Linux socket filter and eBPF instruction construction macros for tools code.

## APIs, State, and Dependencies

It includes `<linux/bpf.h>`, maps argument/context/frame-pointer registers, defines `MAX_BPF_STACK`, and provides initializer macros for ALU, move, endian, load, store, atomic, jump, call, immediate, map-fd, map-value, relative-call, and exit BPF instructions. Each macro expands to one or more `struct bpf_insn` initializers. There is no runtime state.

## Risks and Test Signals

Instruction encoding macros are ABI-sensitive; wrong opcodes, register fields, offsets, or immediate splitting can produce verifier rejection or wrong BPF behavior. Tests should assemble known instruction sequences, compare encodings to expected bytes/fields, and load simple programs through the BPF verifier.
