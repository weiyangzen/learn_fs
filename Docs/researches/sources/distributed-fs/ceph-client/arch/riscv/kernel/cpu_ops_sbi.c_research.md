# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_sbi.c

Purpose: Implements CPU start/stop operations using the SBI Hart State Management extension.

Important APIs/types/functions: Defines `cpu_ops_sbi`, SBI start/stop helpers, boot-data setup for stack/task pointers, and hart status checks.

Control flow: For CPU start, the kernel fills secondary boot data, translates the start address to a physical address as required, and calls `sbi_hsm_hart_start()`. For stop, the dying CPU invokes `sbi_hsm_hart_stop()` and parks if firmware returns unexpectedly.

State and persistence: Uses per-hart boot data shared with early assembly and persistent firmware hart state managed by SBI.

Dependencies and integration points: Depends on SBI HSM, SMP secondary entry in `head.S`, CPU hotplug, physical address helpers, and boot CPU/hart ID mapping.

Risks and test signals: Firmware status handling, physical address conversion, and boot-data lifetime are critical. Test with OpenSBI HSM, hotplug loops, failed hart-start injection, non-linear CPU-to-hart mappings, and suspend/resume interactions.
