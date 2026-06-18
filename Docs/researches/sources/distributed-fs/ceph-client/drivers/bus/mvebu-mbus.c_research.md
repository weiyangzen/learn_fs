# sources/distributed-fs/ceph-client/drivers/bus/mvebu-mbus.c

## Purpose
This driver manages Marvell EBU MBus address decode windows for Kirkwood, Armada 370/XP/375/380, Dove, Orion5x, and MV78xx0 SoCs. It reads SDRAM decode windows, exposes DRAM target information to other Marvell device drivers for DMA setup, allocates/removes CPU-to-device windows, records optional PCIe apertures from device tree, and provides debugfs visibility under `mvebu-mbus`.

## Important APIs, Types, and Functions
The central state is `struct mvebu_mbus_state`, which holds mapped register bases, SoC layout callbacks, PCIe aperture resources, debugfs dentries, coherency state, and suspend snapshots. `struct mvebu_mbus_soc_data` abstracts per-SoC window counts, register offsets, remap capability, SDRAM decode parsing, debug display, and save routines. Exported integration APIs include `mv_mbus_dram_info()`, `mv_mbus_dram_info_nooverlap()`, `mvebu_mbus_add_window_by_id()`, `mvebu_mbus_add_window_remap_by_id()`, `mvebu_mbus_del_window()`, `mvebu_mbus_get_pcie_mem_aperture()`, `mvebu_mbus_get_pcie_io_aperture()`, `mvebu_mbus_get_dram_win_info()`, and `mvebu_mbus_get_io_win_info()`.

## Control Flow
Initialization is either board-file driven through `mvebu_mbus_init()` or device-tree driven through `mvebu_mbus_dt_init()`. The DT path finds a matching MBus node, resolves the `controller` phandle, maps CPU-window and SDRAM-window resources, optionally maps the MBus bridge for suspend/resume, reads PCIe aperture properties, disables all existing CPU windows, builds DRAM target tables, enables sync-barrier support when coherent, and finally installs static windows from `ranges`. Window creation validates power-of-two size, base alignment, overlap exclusion, and remap capability before writing base/control/remap registers.

## State and Persistence
State is process-global in `mbus_state`, which is expected because MBus is a singleton SoC fabric. Hardware programming persists in MMIO registers. Suspend stores all CPU decode windows plus optional bridge registers in `mbus_state.wins`, `mbus_bridge_ctrl`, and `mbus_bridge_base`; resume restores them through registered syscore ops. Debugfs files read live registers rather than cached state.

## Dependencies and Integration Points
The driver depends on early Linux init, OF address parsing, `memblock`, `debugfs`, `syscore`, `ioremap`, and `linux/mbus.h` consumers. It is a prerequisite for platform devices needing MBus windows or device-to-DRAM DMA attributes. Static windows are derived from DT `ranges`; PCIe integration uses optional `pcie-mem-aperture` and `pcie-io-aperture`.

## Risks and Test Signals
The main risks are incorrect DT ranges, overlapping or non-power-of-two windows, missing bridge resources that break suspend/resume, and singleton global state being used before initialization. Useful signals are boot logs for window allocation errors, debugfs `mvebu-mbus/sdram` and `devices` contents, PCIe/resource probing, DMA correctness for Marvell devices, and suspend/resume on bridge-capable Armada SoCs.
