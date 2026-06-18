# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c

### Purpose
Low-level SPU management core for Cell systems. It tracks SPUs, handles SLB and storage faults, requests class interrupts, creates SPU devices/sysfs attributes, exports management operations, and integrates crash shutdown.

### Important APIs, Types, And Functions
Exports `spu_management_ops`, `spu_priv1_ops`, `cbe_spu_info`, `force_sig_fault`, `spu_invalidate_slbs()`, `spu_associate_mm()`, `spu_64k_pages_available()`, `spu_setup_kernel_slbs()`, `spu_init_channels()`, `spu_add/remove_dev_attr*()`. Internal flows include `__spu_trap_data_seg()`, `__spu_trap_data_map()`, three class IRQ handlers, `spu_request_irqs()`, `create_spu()`, `spu_stat_show()`, crash SPU registration, `spu_shutdown()`, and `init_spu_base()`.

### Control Flow
Device init initializes per-node lists, registers the SPU bus, enumerates SPUs through `spu_management_ops`, creates each SPU object, requests class 0/1/2 IRQs, registers sysfs, adds global lists, registers crash shutdown, and initializes affinity. IRQ handlers dispatch class-specific faults/mailbox/stop/DMA callbacks while holding the register lock. SLB/data faults either load SLB entries, hash kernel pages, or call the SPU stop callback for process-context handling.

### State, Persistence, And Dependencies
State includes global SPU lists, per-node `cbe_spu_info`, locks/mutexes, per-SPU mm association, stats, IRQ registrations, sysfs devices, crash snapshots, and syscore shutdown. No durable persistence. Dependencies include SPU management/priv1 ops supplied by platform code, MMU/hash page code, IRQ APIs, sysfs/device core, kexec crash hooks, and Cell SPU register definitions.

### Integration Points
Provides the exported substrate used by spufs, Cell platform code, SPU context switching, coredump, and SPU device attributes.

### Risks
High concurrency risk: global list locking spans IRQ and sleepable contexts; SPU register locks protect fault state; crash shutdown runs in constrained contexts. Fault handling, SLB loading, and callback ordering are hardware-critical.

### Test Signals
Boot Cell/SPU systems, enumerate SPUs, run spufs workloads, generate DMA/storage/SLB faults, inspect sysfs stats, test coredump/crash shutdown, add/remove attributes, and verify suspend/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c -->
