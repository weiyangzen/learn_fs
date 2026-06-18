# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c

## Purpose

`soc15.c` is the AMDGPU common IP implementation for GFX9/SOC15-era devices including Vega, Raven/Raven2/Picasso/Renoir, Arcturus, Aldebaran, and Aqua Vanjaram-class derivatives. It wires the `AMD_IP_BLOCK_TYPE_COMMON` block into the AMDGPU IP lifecycle and installs ASIC-level callbacks used by higher-level device code for BIOS reads, whitelisted register reads, resets, clocks, PCIe counters, doorbells, video codec capability queries, and clock/power gating. The file is not a standalone device driver; it is selected by AMDGPU's ASIC discovery and IP block setup.

## Important APIs, Types, And Functions

Key exported objects are `vega10_common_ip_block`, `soc15_grbm_select()`, `soc15_set_virt_ops()`, and `soc15_program_register_sequence()`. The file defines `soc15_asic_funcs`, `vega20_asic_funcs`, and `aqua_vanjaram_asic_funcs`, selecting doorbell setup and PCIe/statistics behavior by chip family. Indirect register helpers cover UVD context, DIDT, GC CAC, and SE CAC with per-register spinlocks. `soc15_query_video_codecs()` maps VCE/UVD/VCN IP versions to codec arrays. Reset helpers select PCI, BACO, Mode1, Mode2, or link reset depending on module parameters, MP1 IP version, RAS state, XGMI CPU attachment, BACO capability, and suspend/resume state.

## Control Flow

`soc15_common_early_init()` sets NBIO remapping, installs indirect register callbacks, records revision IDs, chooses ASIC functions and CG/PG flags from GC IP version, and initializes SR-IOV mailbox support when running as a VF. `sw_init()` delegates DF initialization and VF mailbox IRQ registration. `hw_init()` programs ASPM, initializes NBIO, optionally remaps HDP registers, enables doorbell apertures, and initializes SDMA doorbell ranges before CP rings use doorbells. Late init enables VF mailbox IRQs and the selfring aperture. Fini/suspend paths reverse doorbell and IRQ state; resume can force an ASIC reset for aborted S3 cases.

## State And Persistence Behavior

Persistent software state is stored in `adev`: `asic_funcs`, register access function tables, `cg_flags`, `pg_flags`, `external_rev_id`, doorbell index/range state, VF mailbox settings, and RAS/NBIO IRQ ownership. Hardware state is written through NBIO/HDP/DF/SMUIO registers, doorbell aperture controls, GRBM selection, PCIe counters, and golden register programming. Several helpers intentionally cache hardware-derived values such as `gb_addr_config` instead of always reading registers.

## Dependencies And Integration Points

The implementation depends on SOC15 register offset tables, NBIO variants, GFX/GMC/MMHUB/GFXHUB/DF/HDP/SMUIO blocks, PSP/DPM reset services, SR-IOV mailbox code, RAS, XGMI, PCIe helpers, and codec capability definitions exposed to userspace through DRM info queries. `soc15_program_register_sequence()` is consumed by per-IP golden-register setup code.

## Risks And Test Signals

Reset selection is the highest-risk logic because it varies by MP1 version, BACO support, RAS firmware version, APU flags, XGMI attachment, and suspend-abort state. CG/PG flag tables are maintenance-sensitive because a wrong bit enables unsupported clock or power gating. Doorbell range ordering affects SDMA, IH, and CP routing. Useful tests are boot/resume/reset on each supported ASIC, SR-IOV VF initialization, RAS recovery with BACO, `debugfs`/ioctl whitelisted register reads, `clk`/power gating state queries, PCIe replay/usage sysfs, video capability queries, and ring tests after doorbell setup.
