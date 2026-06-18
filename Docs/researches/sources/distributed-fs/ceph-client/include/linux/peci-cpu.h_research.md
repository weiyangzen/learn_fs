<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci-cpu.h -->
# sources/distributed-fs/ceph-client/include/linux/peci-cpu.h

## Purpose
Defines CPU-oriented PECI helper constants and function declarations for reading Intel CPU package telemetry, PCI configuration, endpoint PCI configuration, and MMIO over PECI.

## Important APIs, Types, And Functions
- VFM helpers copied from x86 headers encode/decode vendor-family-model values: `VFM_MODEL()`, `VFM_FAMILY()`, `VFM_VENDOR()`, and `VFM_MAKE()`.
- Includes Intel family model definitions from `../../arch/x86/include/asm/intel-family.h`.
- PECI package/config-space indexes include `PECI_PCS_PKG_ID`, package ID params, module temperature, thermal margin, DIMM temperature, temp target, and TDP units.
- Exported functions: `peci_temp_read()`, `peci_pcs_read()`, `peci_pci_local_read()`, `peci_ep_pci_local_read()`, and `peci_mmio_read()`.

## Control Flow
Consumers call the helper matching the desired PECI command. Each helper sends a request to a `struct peci_device` and fills caller-provided output such as raw temperature, package config data, PCI config dword, endpoint PCI config dword, or MMIO dword.

## State And Persistence
This header does not own state. It exposes read-only telemetry/config accessors. Persistent device identity comes from the `peci_device` and CPU vendor-family-model information.

## Dependencies And Integration Points
Depends on Linux integer types, `struct peci_device` from `peci.h`, x86 VFM conventions, and Intel family model constants. Integrates with hwmon, thermal, power, and platform-management drivers that monitor Intel CPUs through PECI.

## Risks And Edge Cases
Risks include using Intel-only VFM assumptions for non-Intel devices, invalid package config indexes/params, segment/bus/device/function/register overflow or alignment issues, PECI transport errors, and interpreting raw temperature or power-unit data without model-specific scaling.

## Test Signals
Probe PECI CPU devices, read package temperature and thermal margin, fetch CPU ID/microcode/package IDs, read local and endpoint PCI config, perform MMIO reads on valid BARs, and verify error returns for unsupported addresses or offline CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci-cpu.h -->
