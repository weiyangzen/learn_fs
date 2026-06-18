# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm32-stub.c

Purpose: implements ARM 32-bit EFI stub platform checks, CPU-entry-state handoff, post-ExitBootServices state capture, and decompressed kernel placement.

Important APIs/types/functions: defines global `efi_entry_state`, `check_platform_features()`, `efi_handle_post_ebs_state()`, `handle_kernel_image()`, and private `get_cpu_state()`.

Control flow: `check_platform_features()` reads CPSR/SCTLR, logs HYP/SVC and MMU state, allocates an `efi_arm_entry_state`, installs it as a Linux EFI config table, and rejects LPAE kernels on CPUs without sufficient memory-model support. `efi_handle_post_ebs_state()` records CPSR/SCTLR after ExitBootServices. `handle_kernel_image()` allocates a low decompression area, computes a 16 MiB-aligned kernel base allowing `TEXT_OFFSET` slack, frees unused pages, and returns image/reserve addresses for the common stub.

State and persistence behavior: CPU entry-state data is allocated from EFI loader data and passed through a config table to the kernel. Reserved decompression memory persists through stub handoff.

Dependencies and integration points: depends on ARM system registers, EFI boot services, `TEXT_OFFSET`, `MAX_UNCOMP_KERNEL_SIZE`, `EFI_PHYS_ALIGN`, and common stub allocation/free flow.

Risks and test signals: wrong alignment or slack handling can place the decompressed kernel where firmware still owns memory. LPAE feature detection must reject incompatible CPUs. Test signals include boot logs with entry mode/MMU state, visible CPU state table in kernel, and successful ARM EFI boot across alignment edge cases.
