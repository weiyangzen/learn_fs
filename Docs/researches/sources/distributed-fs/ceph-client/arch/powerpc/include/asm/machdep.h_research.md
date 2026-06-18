# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/machdep.h

Purpose: defines the PowerPC machine-description callback table used to bind platform-specific boot, IRQ, PCI, time, reset, power management, kexec, suspend, CPU hotplug, and random seed operations.

Important APIs/types/functions: `struct machdep_calls` contains callbacks for probing/setup, exception initialization, time calibration, IRQ discovery, PCI setup and DMA/IOMMU hooks, restart/poweroff/halt, NVRAM access, progress/error logging, CPU die/idle, machine shutdown, kexec, suspend IRQ handling, CPU probe/release, and random seed. `ppc_md`, `machine_id`, `define_machine`, `machine_is`, `log_error`, and `machine_*_initcall` macros form the public interface.

Control flow: early boot selects a machine description, copies it into `ppc_md`, and platform-neutral code dispatches through callbacks. Machine-specific initcall macros gate init functions on `machine_is(mach)`.

State and persistence: `ppc_md` and `machine_id` persist for the boot lifetime. Callback pointers represent platform policy and hardware access paths.

Dependencies and integration points: integrates with boot probing, device tree, PCI, IRQ, DMA/IOMMU, RTC/NVRAM, kexec, suspend, CPU hotplug, and logging subsystems.

Risks: callbacks may be NULL, so callers must respect optional semantics. `machine_is()` warns before `machine_id` initialization. Callback changes can affect all platform code because `ppc_md` is a central dispatch table.

Test signals: boot representative PowerPC platforms, validate machine probe selection, platform-gated initcalls, restart/poweroff/halt, IRQ setup, PCI DMA/IOMMU hooks, suspend/resume, kexec, and error logging.
