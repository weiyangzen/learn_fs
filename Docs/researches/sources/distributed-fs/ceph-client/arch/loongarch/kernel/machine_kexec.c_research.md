## sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec.c

### Purpose
`machine_kexec.c` implements the LoongArch machine-level kexec and crash-kexec handoff. It prepares safe control code, copies command line data to a low safe area, stops secondary CPUs, converts kexec page-list addresses into directly accessible cached virtual addresses, masks interrupts, and jumps into the relocation stub that enters the next kernel.

### Important APIs, Types, And Functions
The public hooks are `machine_kexec_prepare`, `machine_kexec_cleanup`, `machine_shutdown`, `machine_crash_shutdown`, `machine_kexec`, `kexec_reboot`, and `crash_smp_send_stop` under SMP. Key state includes `reboot_code_buffer`, `cpus_in_crash`, `kexec_ready_to_reboot`, and latched EFI/cmdline/system-table/start/indirection addresses. It consumes `relocate_new_kernel`, `relocate_new_kernel_size`, and `kexec_smp_wait` from `relocate_kernel.S`.

### Control Flow
Prepare records EFI arguments, finds or copies the command line, sets `control_code_page` to `KEXEC_CONTROL_CODE`, copies the relocation stub there, and computes the relocated secondary wait function. Normal shutdown on SMP brings possible CPUs online and sends `kexec_shutdown_secondary`, which marks each CPU offline, disables IRQs, waits for `kexec_ready_to_reboot`, then enters the common reboot path. Crash shutdown saves crash CPU registers, sends crash IPIs, waits up to 10 seconds for other CPUs to save state, masks interrupts, and then `machine_kexec` updates indirection entries before releasing CPUs and jumping.

### State, Persistence, And Dependencies
The handoff state persists only through the reboot transition in fixed low physical/cached addresses `0x100000` and `0x108000`. It depends on generic kexec image layout, EFI boot arguments, LoongArch direct-map/cache helpers, crash dump CPU-save APIs, SMP IPI delivery, and the assembly relocation code.

### Integration Points
Generic `kernel/kexec*` calls these machine hooks. `machine_kexec_file.c` populates `image->arch.cmdline_ptr` for file-mode loads. Crash dump integration uses `crash_save_cpu`, `machine_kexec_mask_interrupts`, and crashkernel reservation from setup. Secondary CPUs enter the mailbox wait loop in `relocate_kernel.S`.

### Risks
The fixed safe memory range must remain reserved and truly safe; overlap with firmware, crashkernel, or loaded segments would corrupt handoff code or command line. Page-list virtual conversion mutates `image->head` entries and must preserve kexec flags. SMP crash paths can hang if secondary CPUs fail to service IPIs or if `kexec_ready_to_reboot` is never observed. Logging the command line may expose sensitive boot arguments.

### Test Signals
Validate normal `kexec -e`, file-mode kexec, crash-kexec, SMP secondary parking, CPU hotplug interactions, and EFI argument propagation. Inspect console for EFI/cmdline/start notices, ensure crash dumps contain per-CPU notes, and verify the new kernel receives the expected command line and initrd. Fault injection around missing command line and nonresponding secondary CPUs is useful.
