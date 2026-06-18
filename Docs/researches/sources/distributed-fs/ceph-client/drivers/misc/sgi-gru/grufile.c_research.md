# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufile.c

Purpose: provides `/dev/gru` file operations, mmap setup, user ioctl dispatch, driver initialization, GRU table discovery, TLB IRQ setup, proc/kservices startup, and module teardown.

Important APIs and functions: globals include `gru_base[]`, `gru_start_paddr`, `gru_start_vaddr`, `gru_end_paddr`, `gru_max_gids`, and `gru_stats`. File operations are `gru_file_mmap()` and `gru_file_unlocked_ioctl()`. Initialization helpers include `gru_supported()`, `gru_init_chiplet()`, `gru_init_tables()`, `gru_setup_tlb_irqs()`, `gru_init()`, and `gru_exit()`. VMA close is `gru_vma_close()`.

Control flow: init only acts on supported x86 UV systems before UV3. It derives GRU physical overlay base from UV MMRs, registers misc device, initializes procfs, allocates per-blade GRU state pages, initializes chiplets/resources, sets up per-chiplet TLB IRQs, starts kernel services, and publishes version info. Mmap requires shared writable GSEG-page-aligned mapping, marks VMA IO/PFNMAP/locked/no-copy/no-dump, installs `gru_vm_ops`, and allocates VMA tracking. Ioctls dispatch context creation/options/exception/unload/flush/call-OS/stats/dump/config/ktest requests.

State and persistence: global GRU topology/state persists for module lifetime; per-VMA data tracks thread states and is freed on VMA close after unloading contexts. Hardware IRQ and GRU resource state persists until exit.

Dependencies and integration points: depends on UV hub APIs/MMRs, miscdevice, procfs, IRQ setup, `grumain.c`, `grufault.c`, `grutlbpurge.c`, `grukservices.c`, and `grukdump.c`.

Risks and test signals: init unwind crosses misc/proc/table/IRQ/kernel-service layers. `gru_free_tables()` uses an order based on `struct gru_state * chiplets` while allocation used `sizeof(struct gru_blade_state)`, which should be verified. Tests should cover unsupported platforms as no-op success, mmap alignment/permission rejection, each ioctl dispatch, VMA close unloading all contexts, IRQ setup/teardown on CPUless blades, and repeated module load/unload.
