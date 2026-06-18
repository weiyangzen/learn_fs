# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra194.c

## Purpose
This file is the Tegra194 MC SoC data table. It enumerates Tegra194 memory clients, assigns stream IDs and SID override/security register offsets, defines MC interrupt masks, and exports `tegra194_mc_soc` for the common MC driver. It reuses the Tegra186 MC operations for probe, child population, SID override, and resume.

## Important APIs, Types, And Functions
The principal objects are `tegra194_mc_clients`, `tegra194_mc_intmasks`, and `tegra194_mc_soc`. There are no local functions. The client table covers legacy engines plus Tegra194-specific MIU, NVDLA, PVA, RCE, NVENC1, PCIe, NVDEC1, ISP/VI falcon, and additional read paths. Each client entry records a memory-client ID, a printable name, a `TEGRA194_SID_*` stream ID, and SID override/security offsets.

## Control Flow
At runtime the common MC driver selects `tegra194_mc_soc`, then uses `tegra186_mc_ops`. The inherited probe maps broadcast/channel windows and populates child devices. Device attachment and resume use the table entries here to program SID overrides. Interrupt decode is handled by the common Tegra30-style handlers with the Tegra194 mask, including route-sanity, generalized carveout, MTS, secure, VPR, security-violation, and EMEM decode errors.

## State And Persistence
This file contains only constant descriptors. Hardware state derived from it includes SID override register values, interrupt mask settings, channel register mapping behavior, and high-address error reporting. No file-local state persists; the common MC driver and hardware registers hold all runtime state. Resume behavior is inherited from Tegra186 and reprograms SIDs from this table.

## Dependencies And Integration Points
It depends on `dt-bindings/memory/tegra194-mc.h`, `soc/tegra/mc.h`, and `mc.h`. The SoC descriptor advertises 40-bit addressing, 16 MC channels, high address register support, `client_id_mask = 0xff`, `ch_intmask = 0x00000f00`, `global_intstatus_channel_shift = 8`, common `tegra_mc_icc_ops`, `tegra20_mc_regs`, and `tegra30_mc_irq_handlers`. Device tree interconnect IDs and IOMMU stream IDs must align with this table.

## Risks
The data table is large and manually maintained, so duplicate or incorrect SID offsets are the main risk. Some entries share offsets that may reflect hardware aliasing but should be reviewed carefully during updates. A wrong SID can route DMA through the wrong IOMMU context; a wrong client ID can make ICC, error logging, and SID override target the wrong engine. Because functionality is inherited from Tegra186, changes in `tegra186.c` affect Tegra194 behavior as well.

## Test Signals
Validation should include booting Tegra194 with IOMMU enabled, checking that PCIe, display, VIC, NVDEC/NVENC, NVDLA, PVA, XUSB, EQOS, SDMMC, and BPMP clients DMA without stream-ID faults, and verifying MC error reports identify the expected client names. Suspend/resume should preserve SID overrides. Device tree binding tests should ensure all interconnect client IDs used by peripherals exist in `tegra194_mc_clients`.
