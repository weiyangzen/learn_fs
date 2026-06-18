# sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip.h

## Purpose
Declares minimal Numascale NumaConnect platform detection and PCI initialization hooks.

## Important APIs, Types, And Functions
Exports global `u8 numachip_system` and `int __init pci_numachip_init(void)`.

## Control Flow
Platform detection code sets `numachip_system`, and PCI initialization calls `pci_numachip_init()` during boot on matching systems.

## State And Persistence
`numachip_system` is boot-time platform state that persists for the running kernel. No filesystem persistence.

## Dependencies And Integration Points
Integrates with x86 platform setup, Numachip APIC/CSR code, and PCI initialization.

## Risks And Edge Cases
False platform detection can route PCI or APIC setup through Numachip-specific paths on non-Numachip hardware. Missing init on real hardware can break PCI topology.

## Test Signals
Boot coverage on Numascale systems or emulation, PCI enumeration logs, and non-Numachip boot regression checks are useful.
