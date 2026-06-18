<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbus.h -->
# sources/distributed-fs/ceph-client/include/linux/mbus.h

## Purpose
This header exposes Marvell MBUS DRAM and address-window helpers used by Orion/MVEBU SoC drivers.

## Important APIs, types, and functions
`struct mbus_dram_target_info` describes DRAM target ID and up to four chip-select windows with CS index, MBUS attribute, base, and size. Constants define PCI IO/MEM/WA region flags, no-remap sentinel, and maximum window-name size. APIs include `mv_mbus_dram_info`, `mv_mbus_dram_info_nooverlap`, `mvebu_mbus_get_io_win_info`, `mvebu_mbus_get_pcie_mem_aperture`, `mvebu_mbus_get_pcie_io_aperture`, `mvebu_mbus_get_dram_win_info`, add/delete window helpers, `mvebu_mbus_init`, and `mvebu_mbus_dt_init`, with stubs when unsupported.

## Control flow
Platform code initializes MBUS windows from SoC/DT data. Device drivers query DRAM or IO window attributes and add/remap decode windows for peripherals. On non-Orion or non-MVEBU builds, stubs return NULL or `-EINVAL`.

## State and persistence
The header defines query/update APIs for hardware decode-window state held by the MBUS driver and registers. It stores no state itself.

## Dependencies and integration points
It depends on errno, resources, physical addresses, and architecture Kconfig symbols. It integrates with PCIe, DMA engines, memory controllers, and Marvell platform boot code.

## Risks and test signals
Risks include overlapping windows, stale remap assumptions, ARM32 versus ARM64 stub behavior, and wrong target/attribute pairs causing DMA faults. Test DRAM window discovery, no-overlap variant, PCIe aperture reporting, add/delete/remap windows, and non-MBUS build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbus.h -->
