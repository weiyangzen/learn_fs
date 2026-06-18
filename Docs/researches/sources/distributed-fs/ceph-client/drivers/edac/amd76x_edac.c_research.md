# sources/distributed-fs/ceph-client/drivers/edac/amd76x_edac.c Research

## Purpose
This PCI driver reports ECC memory errors from legacy AMD 76x chipsets, specifically AMD761 and AMD762 front-end bridge devices. It polls chipset PCI config status bits, maps chip-select rows from chipset memory-base registers, and reports CE/UE events through the EDAC memory-controller framework.

## Important APIs, Types, and Functions
Register definitions cover `AMD76X_ECC_MODE_STATUS`, `AMD76X_DRAM_MODE_STATUS`, and `AMD76X_MEM_BASE_ADDR`. `struct amd76x_error_info` snapshots ECC mode/status. `amd76x_get_error_info()` reads and clears pending CE/UE bits. `amd76x_process_error_info()` maps status bits to EDAC corrected or uncorrected events. `amd76x_check()` is the polling callback. `amd76x_init_csrows()` initializes EDAC csrow/dimm metadata from memory base/mask registers. `amd76x_probe1()`, `amd76x_init_one()`, and `amd76x_remove_one()` manage PCI probe/remove. The PCI ID table matches AMD FE gate devices and maps them to AMD761/AMD762 controller names.

## Control Flow
Module init calls `opstate_init()` and registers the PCI driver. Probe reads ECC mode, allocates an EDAC MC with eight virtual chip-select rows and one channel, fills capability fields, initializes csrows from PCI config, clears stale ECC status, registers the MC, and optionally creates a generic EDAC PCI control object. EDAC polling invokes `amd76x_check()`, which snapshots the ECC mode/status register, clears CE/UE status bits by writing back individual bits, then reports uncorrectable and correctable errors using the csrow encoded in the status register. Remove releases generic PCI EDAC state, deletes the MC, and frees it.

## State and Persistence
Driver state is minimal: a global `amd76x_pci` generic PCI EDAC control pointer and the EDAC MC instance attached to the PCI device. Hardware status bits persist in PCI config space until cleared by `amd76x_get_error_info()`. EDAC core persists counters and csrow/dimm metadata.

## Dependencies and Integration Points
The driver depends on PCI, x86 32-bit Kconfig gating, EDAC MC APIs, EDAC PCI generic control support, and legacy AMD chipset PCI IDs. It exposes the module parameter `edac_op_state` for poll/NMI reporting state consistent with other EDAC drivers.

## Risks and Edge Cases
The driver assumes only one instance of this memory-controller type and hardcodes EDAC MC index 0. The chipset only provides row-level location, so reports lack detailed address/channel/syndrome information. It clears status before processing reports, and `amd76x_process_error_info()` trusts row values from hardware status; corrupt row fields could index invalid csrows. The driver is old 32-bit x86 chipset support, so build and runtime coverage is likely sparse.

## Test Signals
Build with `CONFIG_EDAC_AMD76X` on an x86_32 PCI config. Runtime signals are PCI probe on AMD761/AMD762 IDs, EDAC MC registration with populated csrows, polling callbacks, and CE/UE counters changing when chipset ECC status bits are injected or observed. Removal should release both the generic PCI control and MC cleanly.
