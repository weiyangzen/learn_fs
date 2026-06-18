# sources/distributed-fs/ceph-client/arch/x86/include/asm/msi.h

## Purpose
Defines x86-specific MSI message bit layouts, allocation info aliasing, and PCI MSI preparation hooks.

## Important APIs, Types, And Functions
Defines `msi_alloc_info_t`, `pci_msi_prepare()`, packed `arch_msi_msg_data_t`, `arch_msi_msg_addr_lo_t`, `arch_msi_msg_addr_hi_t`, `X86_MSI_BASE_ADDRESS_LOW`, `X86_MSI_BASE_ADDRESS_HIGH`, `x86_msi_msg_get_destid()`, `X86_VECTOR_MSI_FLAGS_SUPPORTED`, and `X86_VECTOR_MSI_FLAGS_REQUIRED`.

## Control Flow
IRQ domain allocation uses `pci_msi_prepare()` to fill architecture allocation data. MSI composition code packs vector, delivery mode, destination mode, trigger/level, redirect hint, and destination ID bits into message address/data fields, with alternate DMAR subhandle layout.

## State And Persistence
No persistent state. MSI messages are programmed into devices and interrupt-remapping tables by callers.

## Dependencies And Integration Points
Depends on x86 hardware IRQ and IRQ domain types plus generic MSI definitions. It integrates with PCI MSI/MSI-X, interrupt remapping, xAPIC/x2APIC destination encoding, and vector domains.

## Risks And Edge Cases
Packed bitfields must match APIC/MSI hardware format and endianness expectations. Extended destination IDs and DMAR formats are easy to encode incorrectly. Required flags must remain aligned with generic MSI core behavior.

## Test Signals
PCI MSI/MSI-X device tests, interrupt remapping tests, high APIC ID systems, dynamic MSI-X allocation, and IRQ affinity tests provide coverage.
