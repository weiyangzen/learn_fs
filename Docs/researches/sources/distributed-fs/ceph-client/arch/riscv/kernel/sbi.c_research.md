<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi.c

Purpose: Implements the RISC-V Supervisor Binary Interface client layer for timers, IPIs, remote fences, firmware features, reset/poweroff, debug console, base extension probing, and legacy v0.1 compatibility.

Important APIs/types/functions: Exposes `sbi_console_putchar/getchar()`, `sbi_shutdown()`, `sbi_set_timer()`, `sbi_send_ipi()`, all `sbi_remote_*fence*()` helpers, `sbi_fwft_set*()`, SRST reboot/poweroff helpers, `sbi_probe_extension()`, firmware ID/version and machine ID getters, `sbi_debug_console_write/read()`, and `sbi_init()`.

Control flow: Initialization probes the SBI spec version, chooses v0.1 or v0.2+ operation tables, discovers supported extensions, installs reset/poweroff hooks, and enables debug console and firmware-feature paths. Runtime helpers translate Linux CPU masks to hart masks, batch remote fence calls over hartmask chunks, and route all work through `__sbi_ecall()`.

State and persistence: Maintains read-mostly spec/implementation metadata, function pointers for timer/IPI/rfence implementations, extension support flags, FWFT availability, and reboot notifier state. Per-call state is in stack-local hart masks and `sbiret` results.

Dependencies and integration points: Central dependency for timer init, SMP/IPI, TLB shootdown, KVM hypervisor fences, suspend/HSM, reset, debug console, and hwprobe machine identifiers.

Risks: v0.1 and v0.2 calling conventions differ sharply; wrong selection breaks early boot. CPU-to-hart mapping and hartmask chunking must not skip offline/large hart IDs. Reset and poweroff behavior is firmware-dependent.

Test signals: Boot on legacy and modern SBI firmware, timer interrupts, SMP IPI/fence stress, SRST reboot/poweroff, DBGC read/write, FWFT feature calls, and KVM HFENCE helpers.

Source read size: 709 lines, 19144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi.c -->
