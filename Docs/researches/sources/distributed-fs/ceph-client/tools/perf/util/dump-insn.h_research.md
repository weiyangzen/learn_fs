# sources/distributed-fs/ceph-client/tools/perf/util/dump-insn.h

## Purpose
This header declares a small architecture-aware instruction dumping interface used by perf code that needs a textual representation of instruction bytes and branch classification without going through full annotation disassembly.

## Important APIs And Types
`MAXINSN` is set to 15, matching the maximum x86 instruction length. `struct perf_insn` carries caller-initialized context: thread, machine, cpumode, 64-bit mode, CPU, and a fixed 256-byte output buffer. The declared APIs are `dump_insn(struct perf_insn *x, u64 ip, u8 *inbuf, int inlen, int *lenp)` and `arch_is_uncond_branch(const unsigned char *buf, size_t len, int x86_64)`.

## Control Flow And Integration
Callers populate `perf_insn` with sample/thread/machine context and pass instruction bytes plus the IP. The implementation, outside this header, is expected to decode or format the instruction into `x->out`, report the consumed length via `lenp`, and classify unconditional branches for the current architecture/mode.

## State And Persistence
The API is stack-friendly and caller-owned. It persists no global state in the header contract; `out` is embedded in the caller-provided object and valid until that object changes.

## Risks And Test Signals
Risks include buffer-size assumptions, incomplete architecture support, and wrong length reporting when fewer than `MAXINSN` bytes are available. Tests should cover short buffers, maximum-length x86 instructions, 32-bit versus 64-bit x86 unconditional branches, non-branch bytes, and integration with sample context where thread or machine is missing.
