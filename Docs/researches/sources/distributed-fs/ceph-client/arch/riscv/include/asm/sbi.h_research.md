<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sbi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sbi.h

Purpose: Declares the Supervisor Binary Interface IDs, data structures, feature flags, and kernel call wrappers used to communicate with RISC-V firmware.

Important APIs/types/functions: Covers SBI extension/function enums for BASE, TIME, IPI, RFENCE, HSM, SRST, SUSP, PMU, DBCN, STA, NACL, FWFT, MPXY, DBTR, legacy v0.1 calls, `struct sbiret`, `sbi_ecall()`, extension probe/version helpers, hart suspend/start/status, rfence helpers, PMU snapshot/event structs, reset, debug console, firmware feature calls, and static-key state.

Control flow: Callers probe extensions, then issue `sbi_ecall()` with extension/function IDs and arguments. Header fallbacks compile to disabled/no-op behavior when SBI is not configured.

State and persistence: Persistent state includes probed SBI version/implementation IDs, extension availability, static keys, PMU shared-memory layout, and firmware-managed hart/timer/reset/debug state.

Dependencies and integration points: Integrates with early boot, timers, IPI, TLB shootdown, CPU hotplug/suspend, perf, console, reset, KVM, and alternatives that read vendor IDs via SBI.

Risks: SBI ABI constants are firmware contracts; wrong IDs or argument ordering can hang CPUs, lose TLB shootdowns, miscount PMU events, or reset the system unexpectedly.

Test signals: OpenSBI/QEMU boots, extension probe tests, SMP IPI/rfence, CPU hotplug/HSM, suspend/resume, PMU perf tests, DBCN console, and reset paths.

Source read size: 707 lines, 21334 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sbi.h -->
