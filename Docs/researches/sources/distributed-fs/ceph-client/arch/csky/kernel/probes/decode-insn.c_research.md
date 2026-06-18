# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.c

Purpose: probe instruction decoding and classification for kprobes and uprobes.

Important APIs/types/functions: functions: `csky_probe_decode_insn`; types: `probe_insn`

Control flow: Runtime flow is organized around `csky_probe_decode_insn`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/kernel.h`, `linux/kprobes.h`, `linux/module.h`, `linux/kallsyms.h`, `asm/sections.h`, `decode-insn.h`, `simulate-insn.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
