# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186.c

## Purpose
This file supplies Tegra186 memory-controller operations and the Tegra186 SoC descriptor. It handles MC register-region mapping for broadcast/channel access, populates child devices such as EMC, programs memory-client stream ID overrides for IOMMU integration, restores overrides on resume, and describes Tegra186 memory clients, interrupts, channels, and address geometry.

## Important APIs, Types, And Functions
`tegra186_mc_ops` provides `.probe`, `.remove`, `.resume`, and `.probe_device`. `tegra186_mc_probe()` maps the broadcast channel and per-channel register windows, with Tegra264-compatible handling for DTs where the SID region is absent and the first resource is already broadcast. `tegra186_mc_client_sid_override()` writes per-client SID override/security registers when firmware permits. `tegra186_mc_probe_device()` reads a device's IOMMU stream ID and interconnect phandles to program matching MC client SIDs. `tegra186_mc_resume()` reapplies default SIDs. `tegra186_mc_soc` exports the client table and MC capabilities.

## Control Flow
Common MC probe invokes `tegra186_mc_probe()`. The function identifies whether a named `sid` resource exists; if so it maps the named `broadcast` region, otherwise it reuses `mc->regs` as broadcast for newer layouts. It allocates and maps `ch0` through `ch3`, then calls `of_platform_populate()` so child EMC devices can bind. During device attachment, `probe_device` obtains the device stream ID via `tegra_dev_iommu_get_stream_id()` and scans `interconnects` entries. For entries targeting the MC node, it finds the matching client ID and writes the SID override. Resume loops over all clients and restores descriptor SIDs.

## State And Persistence
Runtime state includes mapped broadcast and channel register pointers in `struct tegra_mc`, per-client SID override register contents, populated child platform devices, and firmware lock bits in MC security registers. SID overrides are hardware state and must be restored after resume. The file does not allocate persistent private state beyond arrays managed by devm.

## Dependencies And Integration Points
It depends on `soc/tegra/mc.h`, `mc.h`, `dt-bindings/memory/tegra186-mc.h`, of-platform population, IOMMU APIs, and the common MC IRQ/error handling tables. The client table maps `TEGRA186_MEMORY_CLIENT_*` IDs to `TEGRA186_SID_*` values and SID override/security offsets. The SoC descriptor uses `tegra20_mc_regs` and `tegra30_mc_irq_handlers`, 40-bit addressing, four channels, `ch_intmask = 0x0000000f`, and global channel shift zero.

## Risks
SID programming depends on secure firmware policy. If the security register has write access disabled and no override enabled, Linux silently leaves the firmware configuration in place. The `WARN_ON()` in the path that tries to set `MC_SID_STREAMID_SECURITY_OVERRIDE` appears to warn on the condition it is about to fix, which can be noisy if reached. Device tree resource naming is critical: missing channel windows fail probe, while missing broadcast only degrades with a warning. Incorrect interconnect client IDs can leave devices with stale stream IDs and cause IOMMU faults or isolation gaps.

## Test Signals
Boot tests should verify MC probe maps all four channel windows and populates EMC children. IOMMU-enabled tests should confirm client devices with interconnects receive the expected SID override and continue DMA after suspend/resume. Negative tests include firmware-locked SID registers, absent broadcast resource, invalid interconnect client IDs, and channel MC faults decoded through common interrupt handling. `dmesg` should show no unexpected SID override warnings during normal boot.
