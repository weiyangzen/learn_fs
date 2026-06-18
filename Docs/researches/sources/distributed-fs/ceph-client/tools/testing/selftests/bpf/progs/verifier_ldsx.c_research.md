# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ldsx.c

## Purpose

`verifier_ldsx.c` tests signed load-extension (`LDSX`) instructions. It checks S8, S16, and S32 sign extension, verifier range refinement, invalid signed loads from context fields, arena disassembly and exceptions, and CPU-version fallback behavior.

## Important APIs, Types, and Functions

The file includes `bpf_arena_common.h` and defines an `arena` map. Program sections include socket, XDP, tcx ingress, flow_dissector, syscall, and a dummy socket fallback. Helper coverage includes `bpf_arena_alloc_pages`; arena tests use kfunc/root-style setup for allocated arena pages. Expected logs include scalar range after S8 load and invalid context-access messages for sign-extending packet context fields.

## Control Flow

Initial socket programs place negative byte, halfword, or word values on the stack and load them with sign extension, returning negative values. Range tests prove the verifier narrows S8/S16/S32 results. Context tests attempt signed 32-bit loads from fields such as `xdp_md->data`, `data_end`, `data_meta`, and `__sk_buff` equivalents, expecting rejection. Arena syscall programs allocate arena memory and exercise LDSX disassembly, exception, and signed loads from arena pages.

## State and Persistence Behavior

Persistent state is the arena map. Runtime arena pages are allocated during syscall programs and used transiently. Verifier state includes signed load result ranges, context field access permissions, and arena pointer bounds.

## Dependencies and Integration Points

The file depends on compiler/JIT support for the relevant BPF CPU version, arena map support, and program-type context validators for XDP, tcx, and flow dissector.

## Risks and Test Signals

Risks are incorrect sign extension, unsound signed range narrowing, allowing unsupported signed ctx loads, or arena/JIT exception mismatches. Test signals are correct negative return values, expected range log for S8, invalid context access failures, arena successes, and dummy success when CPU v4 support is unavailable.
