# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_wildfire.c

## Purpose
Wildfire large-system platform support with QBB/PCA-aware interrupt masks, per-PCA IRQ registration, vector decoding, PCI routing, and machine-vector registration. The source was read as part of `subset-b-000628` and contains 341 lines.

## Important APIs, Types, and Functions
Defines `wildfire_mv`. Key routines are `wildfire_update_irq_hw`, `wildfire_init_irq_hw`, `wildfire_enable_irq`, `wildfire_disable_irq`, `wildfire_mask_and_ack_irq`, `wildfire_init_irq_per_pca`, `wildfire_init_irq`, `wildfire_device_interrupt`, and `wildfire_map_irq`.

## Control Flow
Init clears or synchronizes interrupt enable registers for each possible PCA, initializes i8259, then iterates existing QBBs and PCAs to register local ISA, summary, SCSI, and PCI IRQ ranges. Runtime vectors encode source QBB, PCA, and IRQ-in-PCA; dispatch converts from PAL vector to the Linux IRQ and calls `handle_irq`.

## State and Persistence Behavior
`cached_irq_mask` is indexed by QBB/PCA and protected by `wildfire_irq_lock`; `doing_init_irq_hw` suppresses nonexistent-PCA diagnostics during bulk init. Hardware state is in PCA interrupt enable/target registers and PIC/DMA state.

## Dependencies
Depends on `core_wildfire.h` topology macros, i8259 helpers, Alpha IRQ core, PCI common lookup, and machine vector setup.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
IRQ numbers carry topology bits; wrong shifts or nonexistent PCA handling breaks all interrupts for a quadrant. Low ISA IRQs use i8259 callbacks in addition to Wildfire masks. Only known PCA bit ranges are registered.

## Test Signals
Boot Wildfire with multiple QBB/PCA combinations, verify each PCA's IRQ range, exercise ISA summary and PCI slot lines, test mask/ack under load, and inspect diagnostics for nonexistent PCA references.
