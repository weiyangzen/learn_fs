# sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h` Defines the arm64 kprobes instruction handler contract and per-probe architecture storage. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
probes_handler_t, struct arch_probe_insn, kprobe_opcode_t, struct arch_specific_insn with api, xol_insn, xol_restore. The file is 27 lines / 549 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Runtime flow is implemented by kprobes: decode an opcode, choose a handler, run out-of-line instruction slots, then restore execution address.

### State, Persistence, And Dependencies
State is per registered kprobe instruction, especially xol_insn and xol_restore. No independent persistence. Depends on asm/insn.h and pt_regs users; integrates with kprobes, uprobes-like decoding, exception stepping, and tracing.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong opcode endianness or restore address corrupts probed control flow; handler prototype drift breaks kprobe dispatch.

### Test Signals
Run kprobes selftests, single-step probes, probes in exception-sensitive code, and CONFIG_KPROBES off builds.
