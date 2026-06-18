# sources/distributed-fs/ceph-client/arch/arm/kernel/machine_kexec.c

Purpose: performs ARM-specific validation, crash shutdown, secondary CPU stopping, and final transition into a kexec or crashdump kernel.

Important APIs/types/functions: `machine_kexec_prepare`, `machine_kexec_cleanup`, `crash_smp_send_stop`, `machine_crash_shutdown`, and `machine_kexec`. It consumes `relocate_new_kernel` and writes `struct kexec_relocate_data` into the control page.

Control flow: prepare computes default `r2` ATAGS/DTB pointer, rejects unsafe SMP systems lacking CPU hotplug, validates segment memory, and detects DTB magic. Crash stop sends async calls to other CPUs, waits up to one second, saves CPU notes, masks interrupts, and proceeds. `machine_kexec` asserts only one CPU is online, copies relocation code with `fncpy`, fills relocation data, converts entry to identity mapping, and calls `soft_restart`.

State and persistence: `waiting_for_crash_ipi` tracks non-panic CPUs; `image->arch.kernel_r2` persists into the next kernel boot contract.

Dependencies and integration: depends on kexec core, memblock, OF FDT headers, SMP hotplug operations, cache flushes, identity mapping, and reboot/soft restart.

Risks: executing kexec with live secondary CPUs can corrupt memory; invalid segment memory or wrong DTB pointer breaks next-kernel boot. Test signals include kexec load/execute, crashkernel boot, SMP stop timeout logs, and DTB handoff validation.
