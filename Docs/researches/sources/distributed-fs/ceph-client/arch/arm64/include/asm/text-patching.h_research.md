# sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h` Declares arm64 instruction read/write/copy/set and synchronized text patching helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
aarch64_insn_read(), aarch64_insn_write(), aarch64_insn_write_literal_u64(), aarch64_insn_set(), aarch64_insn_copy(), aarch64_insn_patch_text_nosync(), aarch64_insn_patch_text(). The file is 17 lines / 544 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Implementations patch instructions directly and optionally coordinate synchronization/cache maintenance for live text changes; this header defines the API.

### State, Persistence, And Dependencies
Persistent effects are modified kernel text and literal data. Header owns no storage. Depends on linux/types; integrates alternatives, ftrace, kprobes, static calls, livepatch, and runtime-const patching.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Text patching must preserve instruction atomicity, cache coherency, W^X policy, and stop-machine/synchronization rules.

### Test Signals
Run alternatives/ftrace/kprobe/static_call/livepatch tests, instruction patch failure tests, and I-cache coherency validation.
