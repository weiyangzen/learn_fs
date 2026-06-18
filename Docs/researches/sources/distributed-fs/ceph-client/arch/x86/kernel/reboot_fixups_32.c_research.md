# sources/distributed-fs/ceph-client/arch/x86/kernel/reboot_fixups_32.c

## Purpose
Provides 32-bit board/chipset-specific warm reset fixups for hardware that does not reliably reboot through the generic keyboard-controller path.

## APIs, Types, And Functions
Implements weak override `mach_reboot_fixups()` for 32-bit builds. Fixup functions include `cs5530a_warm_reset()`, `cs5536_warm_reset()`, `rdc321x_reset()`, and `ce4100_reset()`, selected through `struct device_fixup fixups_table`.

## Control Flow
When generic reboot code reaches the keyboard-controller method, it calls `mach_reboot_fixups()`. This function returns immediately in interrupt context, otherwise iterates known PCI vendor/device IDs, obtains a matching device with `pci_get_device()`, runs the fixup, and drops the reference. Fixups perform chipset-specific reset writes via PCI config, MSR, port CF8/CFC/0x92, or CF9.

## State And Persistence
No persistent private state. Effects are immediate chipset reset requests; if reset succeeds, the function never returns.

## Dependencies And Integration
Depends on PCI enumeration, chipset constants, MSR access, I/O ports, and `reboot.c` weak fixup hook.

## Risks And Test Signals
Because reset writes are hardware-specific, false matches or running in unsafe context could wedge the system. Test signals are successful reboot on Geode/Cyrix/NS/RDC/CE4100 class systems and no regression on systems without matching PCI IDs.
