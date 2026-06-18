# sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-aplic.h

## Purpose
`riscv-aplic.h` defines the RISC-V Advanced Platform-Level Interrupt Controller register map, source modes, MSI target encoding, IDC registers, and limits.

## Important APIs, types, and functions
It defines APLIC limits, domain configuration bits, source configuration fields, M/S-mode MSI config registers and shifts, pending/enable set/clear offsets, MSI generation and target fields, IDC offsets, and TOPI/CLAIMI encoding macros.

## Control flow
The APLIC driver configures domain mode and endianness, programs each source as edge/level/detached, sets or clears pending/enable bits, routes interrupts either through direct IDC delivery or MSI target fields, and claims top pending interrupts through IDC registers.

## State and persistence
State is hardware register state for interrupt sources, pending/enabled bits, MSI address configuration, target priority/guest/hart routing, and IDC delivery/threshold.

## Dependencies and integration points
It depends on bitops and integrates RISC-V platform interrupt delivery with IMSIC/MSI mode, direct IDC mode, irqdomains, and privilege-mode-specific configuration.

## Risks and test signals
Risks include M-mode versus S-mode register selection, source ID bounds, endian set-pending offsets, target-field bit errors, and direct/MSI mode confusion. Tests should cover edge and level sources, enable/disable/pending clear, MSI target programming with IMSIC, direct IDC claim, and big-endian register paths.
