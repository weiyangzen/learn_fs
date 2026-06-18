# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h

### Purpose
`kexec.h` defines ARM64 kexec and crash-kernel architecture limits, register capture helpers, restart entry points, and image metadata used to boot a replacement kernel or crash dump kernel.

### Important APIs, Types, And Functions
It exports `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `crash_setup_regs()`, crash nosave/suspend hooks, `cpu_soft_restart()`, `machine_kexec_post_load()`, `struct kimage_arch`, `kexec_image_ops`, `arch_kimage_file_post_load_cleanup()`, and `load_other_segments()`.

### Control Flow
Normal kexec code prepares `struct kimage`, fills ARM64-specific fields, and later calls the soft restart path with entry, DTB, and boot parameters. Crash paths snapshot current or supplied `pt_regs`, avoid crash-reserved PFNs, and preserve resume/suspend handoff state when crash dump support is enabled.

### State, Persistence, And Dependencies
State is carried in `struct kimage_arch` fields such as DTB memory, EL2 vectors, head buffer, and kernel segment handles. It depends on UAPI kexec constants, `pt_regs`, crash dump configuration, and arm64 restart assembly.

### Integration Points
The generic kexec core, crash dump code, EFI/image loader, and ARM64 CPU reset code consume these declarations. Distributed filesystem workloads depend on this for crash collection rather than normal I/O.

### Risks
Register snapshot mistakes corrupt vmcore diagnostics. Bad segment limits or DTB placement can make the second kernel unbootable. EL2/vector handoff is sensitive to virtualization mode.

### Test Signals
Build `CONFIG_KEXEC`, `CONFIG_KEXEC_FILE`, and `CONFIG_CRASH_DUMP`; perform kexec and kdump boots on VHE/nVHE systems; inspect crash registers and reserved-memory freeing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h -->
