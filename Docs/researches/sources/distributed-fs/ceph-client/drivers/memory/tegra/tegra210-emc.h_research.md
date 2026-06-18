# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc.h

Purpose: This header is the private Tegra210 EMC register and data contract for the Tegra210 external memory controller implementation. It defines the memory-controller register offsets, bit fields, timing-table layouts, refresh modes, runtime state object, inline MMIO helpers, and function prototypes used by the Tegra210 EMC clock-change/training code in sibling implementation files.

Important APIs/types/functions: `struct tegra210_emc_timing` is the central per-frequency timing table, carrying burst, trim, per-channel, VREF, MC, latency, training, and DRAM mode register values. `struct tegra210_emc` owns runtime state: MC pointer, clock, timing table selection, MMIO bases, channel count, DRAM topology, training and refresh timers, clock-change timing, debugfs limits, and the Tegra clock EMC provider. `struct tegra210_emc_sequence` abstracts silicon-revision sequencing with `set_clock` and `periodic_compensation`. Inline helpers `emc_writel`, `emc_readl`, channel variants, `ccfifo_writel`, and `div_o3` standardize register access and rounded division. Exported prototypes cover refresh changes, mode-register reads, clock changes, shadow bypass, timing update, DLL handling, power ramping, compensation, timing lookup/adjustment, and periodic compensation.

Control flow: Consumers load a `tegra210_emc_timing`, adjust or compensate it, program shadow/burst/trim registers through offsets from `struct tegra210_emc_table_register_offsets`, use sequence callbacks for revision-specific clock switching, and wait for hardware update status bits. Refresh and training timers can trigger later reprogramming.

State and persistence: No persistent storage is used. State is in live kernel structures and EMC hardware registers. The most sensitive state is `last`/`next` timing, refresh mode, training values, timers, clock-change delay, and debugfs min/max rate.

Dependencies and integration: Depends on Linux MMIO primitives, bit macros, timers, debugfs, Tegra MC structures, and `tegra210_clk_emc_provider`. It integrates with Tegra EMC sequence files such as `tegra210-emc-r21021.c` and shared Tegra memory-controller code.

Risks and test signals: Register-array sizes and enum indices must match firmware/device-tree timing blobs exactly; off-by-one errors can corrupt DRAM timing. Test signals include successful boot across supported DRAM types, clock-rate transitions under load, refresh derating, periodic training, suspend/resume, and absence of timeout logs from update or MRR paths.
