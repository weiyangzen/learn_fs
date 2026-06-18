## sources/distributed-fs/ceph-client/arch/arm/xen/enlighten.c

### Purpose
Initializes Xen support on ARM guests: detects Xen from DT/ACPI, maps shared info and grant frames, sets event-channel IRQs, registers vCPU info, timekeeping hooks, reboot/poweroff hooks, and exports hypercall symbols.

### Important APIs, Types, And Functions
Key functions include `xen_unmap_domain_gfn_range`, `xen_read_wallclock`, `xen_pvclock_gtod_notify`, `xen_starting_cpu`, `xen_dying_cpu`, `xen_reboot`, `xen_early_init`, `arch_xen_unpopulated_init`, `xen_dt_guest_init`, `xen_acpi_guest_init`, `xen_guest_init`, and `xen_late_init`. Globals include `xen_start_info`, `xen_domain_type`, `HYPERVISOR_shared_info`, `xen_vcpu`, `xen_vcpu_id`, `xen_events_irq`, and `xen_grant_frames`.

### Control Flow
Early boot scans `/hypervisor` DT nodes, records Xen version and features, and sets domain type/flags. Guest init locates callback IRQs, maps the shared info page via `XENMEM_add_to_physmap`, allocates per-CPU vCPU info, sets up grant frames, initializes event channels, requests the per-CPU event IRQ, and registers CPU hotplug startup. Late init installs reboot/poweroff hooks, syncs wallclock for non-initial domains, and starts Xen time/runstate support.

### State, Persistence, And Dependencies
Persistent state is global Xen domain metadata, shared info mapping, per-CPU vCPU pointers, grant frame location, and event IRQ. Dependencies include Xen hypercall interfaces, event channels, grant tables, OF/ACPI parsing, EFI proxy setup, pvclock, cpuidle/cpufreq disablement, and virtio restricted memory access.

### Integration Points
This is the ARM Xen architecture entry point for generic Xen subsystems, timekeeping, interrupts, grant tables, suspend stubs, and module-visible hypercall wrappers.

### Risks
Bad DT/ACPI parsing can leave Xen detected but without an event IRQ or grant-table region. Per-CPU vCPU registration cannot be repeated incorrectly. Shared-info mapping failures are fatal. Clock synchronization hypercalls are deliberately rate-limited.

### Test Signals
Boot dom0 and domU ARM guests via DT and ACPI, exercise CPU hotplug, event channels, grant table I/O, Xen wallclock updates, reboot/poweroff, and EFI-runtime proxy paths.
