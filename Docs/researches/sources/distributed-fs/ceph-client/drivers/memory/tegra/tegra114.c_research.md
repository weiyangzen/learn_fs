# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra114.c

Purpose: Tegra114 SoC data table for the common Tegra memory-controller driver. It enumerates memory clients, latency allowance defaults, SMMU swgroups, reset lines, interrupt masks, and SoC capabilities.

Important APIs/types/functions: the file defines `tegra114_mc_clients[]`, `tegra114_swgroups[]`, `tegra114_groups[]`, `tegra114_smmu_soc`, `tegra114_mc_resets[]`, `tegra114_mc_intmasks[]`, and exported `tegra114_mc_soc`. Client entries map hardware client IDs to names, SMMU enable register bits, latency allowance registers, swgroups, and defaults. Reset entries map DT reset IDs to MC reset control/status bits.

Control flow: `mc.c` selects `tegra114_mc_soc` for compatible `nvidia,tegra114-mc`. During common probe, latency allowance defaults are written from the client table, SMMU setup uses swgroup/group data, IRQ mask enables invalid SMMU page, security violation, and EMEM decode errors, and reset-controller calls use `tegra_mc_reset_ops_common` with the reset table.

State and persistence: no mutable state in this file. Tables describe persistent hardware programming performed by the common driver and SMMU code.

Dependencies and integration: includes Tegra114 memory DT bindings for reset IDs and public/private Tegra MC headers. Integrates with common MC probe, Tegra SMMU, reset framework, error IRQ decoding, and latency allowance setup.

Risks: table correctness is critical: client ID, SMMU bit, latency register, swgroup, and reset bit mismatches cause wrong device attribution or unsafe reset behavior. The DRM SMMU group aggregates several swgroups and must match display/GPU users. Interrupt mask coverage is intentionally narrow compared with newer SoCs.

Test signals: boot Tegra114, verify all memory client IDs decode in MC fault logs, exercise SMMU swgroup enable/disable, assert/deassert each listed reset, check latency allowance register defaults, and trigger masked MC interrupts.
