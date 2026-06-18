# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc.c

## Purpose
Provides comprehensive CO-RE relocation testing. It covers kernel/module BTF, struct flavors, nesting, arrays, primitives, modifiers, pointer-as-array, integer signedness, field existence, bitfields, size/offset relocations, type existence/match/size, type IDs, enum values including 64-bit enum values, and btfgen-generated minimal BTFs.

## Important APIs, types, and functions
Central type is `struct core_reloc_test_case`, with object file, target BTF file, input/output byte blobs, expected failure flags, attach program/raw tracepoint names, optional setup, optional trigger, and testmod requirement. Many macros generate table rows. `setup_type_id_case_*()` parses local and target BTFs to fill expected type IDs. `run_btfgen()` invokes `./bpftool gen min_core_btf`. `run_core_reloc_tests()` opens BPF objects with optional `btf_custom_path`, loads, mmaps `.bss`, copies input, attaches raw tracepoint/tp_btf, triggers, and compares output bytes.

## Control flow and state
`test_core_reloc()` runs the table directly; `test_core_reloc_btfgen()` reruns supported cases through generated minimal BTF files. Each subtest may skip if it requires unavailable testmod, lacks target BTF for btfgen, or marks btfgen failure. Runtime state includes temporary `/tmp/core_reloc.btf.*`, mmaped `.bss` struct `data`, BPF object/link/map handles, and expected blobs from static table data. Cleanup unmaps, removes temp BTF, destroys links, and closes objects per case.

## Dependencies and integration points
Depends on many generated `.bpf.o` and `btf__core_reloc_*.bpf.o` files, vmlinux/module BTF, optional `bpf_testmod`, `bpftool`, libbpf BTF APIs, raw tracepoint attachment, and shared CO-RE type definitions. It is a high-value integration point between libbpf relocation logic and kernel verifier/runtime execution.

## Risks and test signals
Risks include brittle expected byte blobs, missing BTF files, absent `bpftool`, module availability, and table entries whose failure semantics differ between direct and btfgen modes. Passing signals are successful load/attach for positive cases, expected load failures for negative cases, no BPF-set skip flag, and exact `memcmp()` of BSS output against expected output.
