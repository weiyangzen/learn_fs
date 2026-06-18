# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pci-defs.h

## Purpose
`cvmx-pci-defs.h` defines the register map and bitfield views for the Octeon PCI block and its PCI configuration-space facade. It is the companion view to NPI PCI registers: macros here are mostly offsets for PCI config/control registers, while NPI callers often wrap them with NPI accessors.

## Important APIs, Types, and Constants
- Register macros cover PCI config DWORDs (`CVMX_PCI_CFG00` through selected high config registers), BAR1 index entries, BIST, counters, second control/status register, doorbells, DMA count/interrupt/time registers, packet credit/sent counters, MSI receive, read command policy, SCM/TSR, and indirect window access.
- `union cvmx_pci_cfg*` types represent standard PCI command/status, BAR, subsystem/vendor, capability, MSI, and Octeon-specific config/control fields.
- `cvmx_pci_bar1_indexx` maps BAR1 windows with address index, endian, cache, and valid-style fields used by host setup to expose low memory or remap high memory.
- Interrupt unions (`cvmx_pci_int_sum`, `cvmx_pci_int_enb`, and `*2` variants) include family-specific layouts for legacy PCI interrupt conditions.
- DMA/packet unions expose counters, thresholds, doorbell payloads, packet credits, and timing interrupt thresholds.

## Control Flow
The header contains no functions. Register access flow is external: PCI host setup code reads a config/control union, mutates fields, writes via `octeon_npi_write32()` or CSR helpers, and sometimes polls counter/status bits.

## State and Persistence Behavior
The file describes hardware state in PCI config space, BAR windows, DMA engines, doorbells, interrupt latches, read timeout/configuration registers, and indirect access windows. These values persist in hardware until reset or driver modification and are visible to both the Octeon CPU and external PCI peers.

## Dependencies and Integration Points
- Depends on fixed-width integers, `CVMX_ADD_IO_SEG` for the read-timeout macro, and `__BIG_ENDIAN_BITFIELD`.
- Heavily consumed by `arch/mips/pci/pci-octeon.c`, which programs PCI command/status, control status, BAR registers, BAR1 index table, read command behavior, and interrupt summary clearing during platform PCI initialization.
- Integrated with `cvmx-npi-defs.h`, since many active call sites access the PCI register set through `CVMX_NPI_PCI_*` addresses and NPI 32-bit accessor functions.

## Risks
- Config-space field definitions are ABI-critical. Incorrect command/status, BAR, MSI, or capability fields can break enumeration or expose invalid memory windows to PCI devices.
- Some registers are 32-bit config DWORDs represented inside 64-bit unions; using the wrong access width can truncate, preserve stale high bits, or perform unintended side effects.
- BAR1 index fields directly control memory exposure, so address/caching/endian mistakes can cause DMA corruption.
- Interrupt summary registers can be write-to-clear; writing a raw mask based on the wrong struct can lose diagnostics or leave interrupts unhandled.

## Test Signals
- PCI enumeration on Octeon hardware should discover expected devices, assign BARs, and pass config read/write checks.
- DMA mapping tests should validate BAR1 translation and access from PCI peers.
- Regression signals include PCI master/target aborts, wrong vendor/device/config values, stuck interrupt bits, packet credit counters not moving, or boot-time hangs in `pci-octeon.c`.
