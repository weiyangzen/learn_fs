# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sb1250.c

## Purpose
Defines SiByte BCM1250/HT/SP1011 PCI quirks for timeout, class, and DMA addressing limitations.

## Important APIs, Types, And Functions
Fixups are `quirk_sb1250_pci`, `quirk_sb1250_pci_dac`, `quirk_sb1250_ht`, and `quirk_sp1011`. Helper `sb1250_bus_dma_limit` walks devices under the host bridge.

## Control Flow
Early quirks set TRDY timeouts and reclassify the HT bridge as normal PCI bridge. Final DAC quirk walks the bus and limits devices to 32-bit DMA except the HT bridge's subordinate bus range, which supports wider addressing.

## State And Persistence
Persists device DMA limits in `dev->dev.bus_dma_limit` and writes bridge timeout registers. Temporary exclude state is stack-local during bus walk.

## Dependencies And Integration Points
Depends on PCI fixup registration, DMA mask definitions, and SiByte/SP1011 device IDs.

## Risks And Edge Cases
DMA limit propagation is subtle: incorrect exclusion of HT subordinate buses can either break 64-bit-capable devices or allow unsafe DAC on a 32-bit bus. Assumes `dev->subordinate` exists for the HT bridge.

## Test Signals
PCI enumeration with devices behind native PCI and HT bridges, DMA mask checks, and driver DMA tests are the main validation signals.
