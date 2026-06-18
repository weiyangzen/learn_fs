## sources/distributed-fs/ceph-client/arch/loongarch/kernel/reset.c

### Purpose
`reset.c` implements LoongArch halt, power-off, and restart machine operations. It stops other CPUs, disables local interrupts where appropriate, calls generic power/restart notifiers, and falls back to EFI, ACPI, or idle loops.

### Important APIs, Types, And Functions
The file defines exported `pm_power_off`, plus `machine_halt`, `machine_power_off`, and `machine_restart`. It integrates with `smp_send_stop`, `do_kernel_power_off`, `do_kernel_restart`, `efi.reset_system`, `efi_reboot`, `acpi_reboot`, and `enable_pci_wakeup`.

### Control Flow
All three operations stop SMP peers under `CONFIG_SMP`. Halt disables interrupts and interrupt masks, prints a safe-power-off message, flushes consoles, and idles forever. Power-off enables PCI wakeup under ACPI/PM, calls generic power-off hooks, attempts EFI shutdown, then idles. Restart calls generic restart hooks, chooses warm EFI reboot for pending capsules or cold otherwise, falls back to ACPI reboot, then idles.

### State, Persistence, And Dependencies
No persistent local state beyond `pm_power_off`. Machine state changes are external firmware/hardware side effects. Dependencies include SMP stop reliability, EFI runtime services, ACPI reboot support, PM wakeup setup, and console flushing.

### Integration Points
Generic reboot and power management code calls these architecture hooks. Platform drivers may assign `pm_power_off` through the exported symbol.

### Risks
If firmware reset calls return, the CPU remains in an idle loop with peers stopped. Restart ordering between generic notifiers, EFI capsule handling, and ACPI fallback affects firmware update flows. Halt disables local IRQs before console flush on panic-pending state, so console driver behavior matters.

### Test Signals
Test `reboot`, `poweroff`, `halt`, EFI capsule reboot, ACPI reboot fallback, SMP stop behavior, and wakeup-enabled poweroff. Verify no CPU continues running after stop and consoles flush expected messages.
