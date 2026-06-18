# sources/distributed-fs/ceph-client/tools/perf/util/sample.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample.c` implements lifecycle helpers for `struct perf_sample` and an instruction-fetch helper that copies the sampled instruction bytes from a thread's address space.

## Important APIs, Types, and Functions

Public functions are `perf_sample__init`, `perf_sample__exit`, `perf_sample__user_regs`, `perf_sample__intr_regs`, and `perf_sample__fetch_insn`. Internal helper `elf_machine_max_instruction_length` maps ELF machine types to maximum instruction byte lengths.

## Control Flow

Initialization either zeroes the entire sample or resets only pointer/lifetime fields for reuse. Exit frees lazily allocated user/intr register dumps and a merged callchain if owned. Register accessors lazily allocate `regs_dump` objects and log allocation failures.

`perf_sample__fetch_insn` returns early if there is no IP or an instruction is already present. It determines the thread's ELF machine, chooses a maximum length, copies bytes from the thread/machine at the sample IP, stores the copied length, and refines x86/x86_64 length using the x86 instruction decoder when possible.

## State and Persistence Behavior

The functions mutate caller-owned `struct perf_sample`. Some sample members are pointers into an original perf event and are not owned here; only lazily allocated register dumps and merged callchains are freed. No persistent state is written.

## Dependencies and Integration Points

It depends on sample definitions, perf debug, thread/machine memory access, Linux zalloc, ELF machine constants, and the x86 instruction decoder. It is used by event parsing, scripting, auxtrace, and reporting paths that need normalized sample state.

## Risks and Edge Cases

Partial initialization with `all=false` requires the rest of the sample to already be in a known state. Instruction length is architecture heuristic except for x86 decoder refinement. Failed memory reads silently leave `insn_len` zero. The helper uses `MAX_INSN` as a fallback and must not overrun the fixed `insn` array.

## Test Signals

Tests should cover full and partial initialization, exit freeing only owned fields, lazy register allocation failure/success, instruction fetch for fixed-length and variable-length architectures, x86 decoder refinement, no-IP early return, already-populated early return, and failed `thread__memcpy` behavior.
