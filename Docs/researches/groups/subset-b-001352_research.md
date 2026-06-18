# Research: subset-b-001352

This grouped report covers AMDGPU Navi/NBIO/NBIF common support files. Each section is source-tree aligned and wrapped with markers consumed by the reconciliation splitter.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c

## Purpose
`nbif_v6_3_1.c` implements the NBIF/NBIO service table for NBIF 6.3.1-family hardware, including HDP flush remapping, revision and memory-size discovery, MC aperture enablement, doorbell routing for SDMA/VCN/GC/IH, interrupt host control, ASPM/LTR programming, ROM offset lookup, MMIO remap selection, and ATHUB RAS event interrupt handling.

## Important APIs, Types, And Functions
The exported `nbif_v6_3_1_hdp_flush_reg`, `nbif_v6_3_1_funcs`, and `nbif_v6_3_1_ras` objects are consumed by ASIC setup code through `struct amdgpu_nbio_funcs` and `struct amdgpu_nbio_ras`. Core callbacks include `get_rev_id`, `mc_access_enable`, `sdma_doorbell_range`, `vcn_doorbell_range`, `gc_doorbell_init`, `ih_doorbell_range`, `ih_control`, `program_aspm`, `get_rom_offset`, and `set_reg_remap`. The file has explicit alternate register definitions for IP version `7.11.4`, including GDC S2A doorbell and strap registers.

## Control Flow
During common hardware init, the selected NBIO ops call `set_reg_remap()`, `program_aspm()`, `init_registers()`, optional HDP remap, and doorbell aperture enablement. Doorbell callbacks program S2A entries with AWID/range/upper-address selectors: SDMA instance 0 uses port 2, VCN instances use ports 4/5, GC writes two fixed entries, and IH uses port 1. Runtime interrupt setup calls `init_ras_err_event_athub_interrupt()`, while the no-BIF-ring handler polls and clears the doorbell interrupt status before invoking global RAS handling.

## State And Persistence
State is MMIO-backed in NBIF/NBIO, PCIE, PCI config space, and `adev->rmmio_remap`. The self-ring aperture uses `adev->doorbell.base`. No disk persistence exists; settings survive only until GPU reset or driver teardown.

## Dependencies And Integration Points
The file depends on AMDGPU core device state, generated NBIF/PCIE register headers, KFD MMIO remap offsets, PCIe capability helpers, SOC21 BIF interrupt IDs, and RAS global ISR dispatch.

## Risks
IP `7.11.4` register special-casing is easy to miss and would send doorbells or strap reads to the wrong offsets. Empty clock-gating callbacks mean callers must not assume BIF MGCG/LS state changes are active. The ASPM path touches both PCI config and NBIF/PCIE registers, so bad LTR path assumptions can break link power management. The source snapshot also contains duplicated text in the self-ring aperture expression, a maintenance signal worth checking against upstream.

## Test Signals
Useful signals are successful GPU init, KFD HDP flush remap visibility, SDMA/VCN/GC/IH ring doorbells working, `lspci`/power traces showing expected ASPM/LTR behavior, and RAS ATHUB interrupts clearing without repeated storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.h

## Purpose
`nbif_v6_3_1.h` is the public declaration point for the NBIF 6.3.1 implementation.

## Important APIs, Types, And Functions
It includes `soc15_common.h` for `struct nbio_hdp_flush_reg`, `struct amdgpu_nbio_funcs`, and `struct amdgpu_nbio_ras`, then declares `nbif_v6_3_1_hdp_flush_reg`, `nbif_v6_3_1_funcs`, and `nbif_v6_3_1_ras`.

## Control Flow
The header has no runtime control flow. ASIC selection code includes it and assigns the exported tables to `adev->nbio` when NBIF 6.3.1 support is needed.

## State And Persistence
It owns no state; the declared objects live in the C file and are process-lifetime kernel data.

## Dependencies And Integration Points
The integration point is the SOC15/NBIO common abstraction used by `nv.c`, SOC21 common setup, and RAS initialization.

## Risks
Because the header exposes the RAS object as mutable `struct amdgpu_nbio_ras`, changes to the struct layout or object name must stay synchronized with the implementation and ASIC dispatch tables.

## Test Signals
Compile/link success confirms symbol names and types match. Runtime confirmation comes indirectly from selecting `nbif_v6_3_1_funcs` and observing working NBIO/RAS callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c

## Purpose
`nbio_v2_3.c` implements NBIO 2.3 services for Navi-era devices. It handles register remap, revision/memory discovery, framebuffer access gating, SDMA and VCN doorbells, IH setup, BIF clock/light-sleep gating, ASPM/LTR programming, Navi PCIe link workarounds, doorbell interrupt clearing, and MMIO remap setup.

## Important APIs, Types, And Functions
The exported surfaces are `nbio_v2_3_hdp_flush_reg` and `nbio_v2_3_funcs`. Important callbacks include `nbio_v2_3_get_rev_id()`, `mc_access_enable()`, `get_memsize()`, `sdma_doorbell_range()`, `vcn_doorbell_range()`, `ih_control()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `enable_aspm()`, `program_aspm()`, `apply_lc_spc_mode_wa()`, `apply_l1_link_width_reconfig_wa()`, and `clear_doorbell_interrupt()`.

## Control Flow
Hardware init programs PCIe request-size fields, applies optional link workarounds, programs ASPM when enabled by policy, remaps HDP flush registers, and enables doorbell apertures. Doorbell functions choose SDMA0-3 and MMSCH0/1 registers, then set offset and size fields. ASPM setup temporarily disables L0s/L1 and LTR, configures strap/timer/LTR capability registers, optionally programs LTR if the upstream path supports it, and then restores link inactivity settings.

## State And Persistence
The file writes PCIe/NBIO registers and `adev->rmmio_remap`. SR-IOV VFs force revision ID to zero and use a VF HDP coherency-flush register for remap. State is reset-scoped, not persistent.

## Dependencies And Integration Points
It depends on generated NBIO 2.3 headers, `amdgpu_device_should_use_aspm()`, PCI device removability for Thunderbolt timing, KFD remap constants, `dev_is_removable()`, and SOC15 indirect PCIe accessors.

## Risks
ASPM and LTR programming is hardware-sensitive and can affect link stability. SDMA instance selection assumes up to four SDMA doorbell registers. Navi10-specific link-width workarounds should not leak to later ASICs. Doorbell interrupt clearing only applies to NBIO `3.3.0`, so regressions may appear only on that IP.

## Test Signals
Look for clean Navi boot, correct `adev->rev_id`, working SDMA/VCN/IH interrupts, ASPM state transitions on suspend/resume, no stuck doorbell interrupt after reset, and PCIe link width/power traces matching expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.h

## Purpose
`nbio_v2_3.h` declares the NBIO 2.3 register flush table and callback table.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and declares `nbio_v2_3_hdp_flush_reg` plus `nbio_v2_3_funcs`.

## Control Flow
There is no executable flow; ASIC-common code includes this header to bind NBIO 2.3 operations into `adev->nbio`.

## State And Persistence
No local state exists. The declarations refer to constant global tables in `nbio_v2_3.c`.

## Dependencies And Integration Points
The header is used by `nv.c`, which includes it directly and relies on the generic NBIO function contract.

## Risks
The minimal declaration surface is stable, but any callback added in the C file remains invisible unless it is reachable through `struct amdgpu_nbio_funcs`.

## Test Signals
Build/link success and successful Navi common early init are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c

## Purpose
`nbio_v4_3.c` provides NBIO 4.3 operations for newer SOC21-style devices, including S2A doorbell routing, HDP remap, ROM offset lookup, BIF clock/light-sleep control, ASPM/LTR programming for selected PCIe IPs, SR-IOV no-op doorbell variants, and ATHUB RAS event interrupt registration/handling.

## Important APIs, Types, And Functions
Exports are `nbio_v4_3_hdp_flush_reg`, `nbio_v4_3_funcs`, `nbio_v4_3_sriov_funcs`, and `nbio_v4_3_ras`. Key callbacks include `gc_doorbell_init()`, `get_rom_offset()`, `program_aspm()`, `set_reg_remap()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, and the RAS functions around `nbio_v4_3_ras_err_event_athub_irq_funcs`.

## Control Flow
Normal init sets the remap hole, initializes soft-reset strap state for NBIO `4.3.0`, programs PCIe power management when the PCIE IP is `7.4.0` or `7.6.0`, remaps HDP flush registers, and enables doorbells. Doorbell programming is S2A based: SDMA instance 0 uses port 2, VCN uses ports 4/5, GC writes fixed entries, and IH uses port 1. SR-IOV ops keep read/control callbacks but replace doorbell programming with no-ops, leaving host control intact.

## State And Persistence
The code mutates NBIO registers, PCIe config-like registers, the MMIO remap fields, and `adev->nbio` interrupt descriptors. State is volatile across reset.

## Dependencies And Integration Points
It depends on generated NBIO 4.3 headers, SOC21 BIF interrupt IDs, `amdgpu_irq_add_id()`, KFD remap constants, RAS global ISR, and PCIe ASPM build configuration.

## Risks
Using the regular ops in SR-IOV would program guest-controlled doorbells that should be host-owned. RAS processing assumes BIF ring is disabled and uses status polling/clearing, so missed clear bits can cause repeated interrupts. ASPM only runs for selected PCIe IP versions and may silently do nothing elsewhere.

## Test Signals
Validate bare-metal and SR-IOV doorbell behavior separately, RAS ATHUB interrupt registration under SOC21 client IDs, VCN/SDMA ring progress, ROM offset reads, and ASPM/LTR behavior on supported PCIE IPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.h

## Purpose
`nbio_v4_3.h` declares the NBIO 4.3 normal and SR-IOV operation tables plus RAS integration object.

## Important APIs, Types, And Functions
It declares `nbio_v4_3_hdp_flush_reg`, `nbio_v4_3_funcs`, `nbio_v4_3_sriov_funcs`, and `nbio_v4_3_ras`.

## Control Flow
The header has no code path. Device setup selects either the normal or SR-IOV function table according to virtualization mode, and RAS setup consumes `nbio_v4_3_ras` when supported.

## State And Persistence
No state is owned by the header; it exposes global objects defined in the C file.

## Dependencies And Integration Points
It depends on the common SOC15 NBIO/RAS types and is integrated by ASIC-specific common init logic.

## Risks
Normal and SR-IOV tables must remain distinct. If a caller only includes this header and chooses the wrong table, host/guest doorbell ownership can break.

## Test Signals
Compile/link coverage plus runtime selection of `nbio_v4_3_sriov_funcs` in VF mode are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c

## Purpose
`nbio_v6_1.c` is the Vega10-era NBIO implementation for SOC15 common code. It supplies HDP flush offsets/masks, revision/memory-size reads, framebuffer access gating, SDMA/IH doorbell programming, interrupt host setup, BIF medium-grain clock gating/light sleep, PCIe request ordering setup, ASPM/LTR programming, and MMIO remap setup.

## Important APIs, Types, And Functions
The file exports `nbio_v6_1_hdp_flush_reg` and `nbio_v6_1_funcs`. Important callbacks are `nbio_v6_1_init_registers()`, `program_aspm()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `get_clockgating_state()`, `ih_control()`, `enable_doorbell_selfring_aperture()`, and `set_reg_remap()`.

## Control Flow
Common init invokes register remap, PCIe ASPM setup, NBIO register init, optional HDP remap, and doorbell aperture enablement. The init path sets software max-read-request controls and disables slave ordering. Doorbell setup writes SDMA0/1 and IH range registers. Clock-gating callbacks read/modify/write PCIE SMN registers according to `adev->cg_flags`.

## State And Persistence
State is in NBIO/PCIE registers and `adev->rmmio_remap`. Doorbell self-ring writes the physical doorbell base into GPA aperture registers. There is no persistent storage.

## Dependencies And Integration Points
It depends on generated NBIO 6.1 headers, Vega10 enum definitions, KFD remap constants, SOC15 register macros, and PCIe ASPM build-time support.

## Risks
The implementation assumes two SDMA instances and no VCN callback. ASPM/LTR values are hard-coded for this generation. If `PAGE_SIZE` exceeds 4 KiB or SR-IOV is active, the remap path falls back to VF HDP coherency-flush offsets, affecting user MMIO exposure.

## Test Signals
Signals include Vega boot without NBIO init errors, correct HDP flush behavior, functioning SDMA/IH doorbells, BIF MGCG/LS flags matching register state, and suspend/resume without PCIe link failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.h

## Purpose
`nbio_v6_1.h` declares the NBIO 6.1 callback table and HDP flush table.

## Important APIs, Types, And Functions
It exposes `nbio_v6_1_hdp_flush_reg` and `nbio_v6_1_funcs`.

## Control Flow
No runtime flow exists in the header. SOC15 common code includes it to install NBIO 6.1 callbacks for matching ASICs.

## State And Persistence
The header owns no mutable state. The declared objects are constant global tables in `nbio_v6_1.c`.

## Dependencies And Integration Points
The only dependency is `soc15_common.h`, which supplies the shared NBIO table structures.

## Risks
Any consumer needing RAS or VCN-specific NBIO 6.1 hooks will not find them here; the implementation only advertises the base function table.

## Test Signals
Compile/link success and a device selecting `nbio_v6_1_funcs` during common init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c

## Purpose
`nbio_v7_0.c` implements NBIO 7.0 support for early SOC15/Navi-adjacent devices. It provides basic memory/revision access, SDMA/VCN/IH doorbell programming, HDP flush mapping, SYSHUB-assisted clock gating, light sleep control, and a small init workaround for NBIO `2.5.0`.

## Important APIs, Types, And Functions
Exports are `nbio_v7_0_hdp_flush_reg` and `nbio_v7_0_funcs`. Notable helpers include `nbio_7_0_read_syshub_ind_mmr()`, `nbio_7_0_write_syshub_ind_mmr()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `ih_control()`, `init_registers()`, and `set_reg_remap()`.

## Control Flow
Hardware init programs remap state, runs `init_registers()`, remaps HDP flush registers, and enables doorbell aperture. Clock gating writes both NBIF LCLK and indirect SYSHUB SOCCLK/SHUBCLK registers. Doorbell setup programs two SDMA ranges, one MMSCH/VCN range, and an IH range. Self-ring aperture callback is intentionally empty for this generation.

## State And Persistence
State is volatile NBIO, PCIE, SYSHUB, and MMIO-remap configuration. `set_reg_remap()` uses the generic MMIO hole on bare metal and HDP coherency flush offset in VF or large-page cases.

## Dependencies And Integration Points
It depends on generated NBIO 7.0 register files, Vega10 enum definitions, KFD remap constants, and SOC15 common init.

## Risks
The empty self-ring aperture callback means late common init can call it without effect. Clock-gating state reporting reads `smnCPM_CONTROL` while enablement uses NBIF/SYSHUB paths, so state flags may not cover every programmed bit. The `2.5.0` strap workaround is narrow and should be tested on that IP only.

## Test Signals
Useful tests are SDMA/VCN/IH ring startup, HDP flush remap reads, clock-gating flag transitions, and NBIO `2.5.0` reset behavior after the strap bit clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.h

## Purpose
`nbio_v7_0.h` declares NBIO 7.0 HDP flush and function tables.

## Important APIs, Types, And Functions
It exposes `nbio_v7_0_hdp_flush_reg` and `nbio_v7_0_funcs`.

## Control Flow
No executable code exists. ASIC dispatch includes this header to select NBIO 7.0 behavior.

## State And Persistence
The header owns no state and only references constant implementation objects.

## Dependencies And Integration Points
It depends on `soc15_common.h` and integrates through the shared `amdgpu_nbio_funcs` contract.

## Risks
Consumers must not assume self-ring aperture support just because the function table contains a callback; in this version it is empty.

## Test Signals
Build success and runtime NBIO 7.0 table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c

## Purpose
`nbio_v7_11.c` supports NBIO 7.11 devices with PF1/BIF1 register layout, USB4-flavored PCIe control registers, VPE doorbell ranges, VCN0/1 doorbells, clock/light-sleep control, and a 0x44000 MMIO remap hole.

## Important APIs, Types, And Functions
The file exports `nbio_v7_11_hdp_flush_reg` and `nbio_v7_11_funcs`. Important callbacks include `vpe_doorbell_range()`, `vcn_doorbell_range()`, `sdma_doorbell_range()`, `enable_doorbell_selfring_aperture()`, `ih_control()`, `init_registers()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `get_pcie_port_index_offset()`, and `set_reg_remap()`.

## Control Flow
Common init programs PF1-oriented remap/PCIe offsets, sets request-size fields, clears a strap bit for NBIO 7.11.0 through 7.11.4, remaps HDP flush registers, and enables doorbells. Doorbell paths use PCIe-port reads/writes for CSDMA, VPE/VPE1, VCN0/VCN1, and IH ranges. Clock gating writes the BIF_BIF256_CI256_RC3X4_USB4 CPM register; light sleep writes PCIe CNTL2 and TX_POWER_CTRL_1.

## State And Persistence
The code mutates PF1 HDP flush, PCIe port, BIF1 interrupt, doorbell self-ring, and request-size registers. State persists only until reset.

## Dependencies And Integration Points
It depends on generated NBIO 7.11 headers, KFD remap offsets, SOC15 register macros, and common NBIO dispatch. The header declares a `nbio_v7_11_ras_funcs` object, but this C file only defines the base function and flush tables.

## Risks
PF1 register naming makes accidental use of PF0 offsets a high-risk class. The VPE callback is additional surface compared with earlier versions. The header's RAS declaration appears stale or externally satisfied; a build configuration expecting it from this file would fail.

## Test Signals
Test CSDMA, VPE, VCN0/1, and IH doorbell operation; verify PF1 HDP flush masks; check BIF1 interrupt setup; and ensure NBIO 7.11.x strap clearing does not regress reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.h

## Purpose
`nbio_v7_11.h` declares NBIO 7.11 exported tables.

## Important APIs, Types, And Functions
It declares `nbio_v7_11_hdp_flush_reg`, `nbio_v7_11_funcs`, and `nbio_v7_11_ras_funcs`.

## Control Flow
The header has no runtime flow. ASIC code includes it to access NBIO 7.11 callbacks.

## State And Persistence
No state is defined here; all objects are external.

## Dependencies And Integration Points
It depends on `soc15_common.h` and the common NBIO/RAS type definitions.

## Risks
The declaration of `nbio_v7_11_ras_funcs` is not matched by a visible definition in `nbio_v7_11.c` in this snapshot. That may be an unused stale declaration or a cross-file symbol expectation that needs link-time verification.

## Test Signals
Compile/link is the primary signal, especially with configs that reference NBIO 7.11 RAS functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c

## Purpose
`nbio_v7_2.c` implements NBIO 7.2/7.3/7.5-style services with special register aliases for Yellow Carp-like IPs. It handles HDP remap, revision and memory-size discovery, MC access enablement, SDMA/VCN/IH doorbells through PCIe-port access, PCIe-port index/data offsets, clock/light-sleep gating, request-size setup, and reset strap clearing.

## Important APIs, Types, And Functions
Exports are `nbio_v7_2_hdp_flush_reg` and `nbio_v7_2_funcs`. Key callbacks include `get_pcie_port_index_offset()`, `get_pcie_port_data_offset()`, `update_medium_grain_light_sleep()`, `init_registers()`, `set_reg_remap()`, and IP-version-specific `get_rev_id()` / `mc_access_enable()`.

## Control Flow
The code switches on NBIO IP version for strap and FB enable registers on `7.2.1`, `7.3.0`, and `7.5.0`, and for strap clearing on `7.3.0` and `7.5.1`. Doorbell paths use `RREG32_PCIE_PORT()`/`WREG32_PCIE_PORT()` for GDC0 SDMA, VCN, and IH ranges. Light sleep uses a richer path for `7.2.1/7.3.0/7.5.0`, programming both PCIE_CNTL2 and `BIF1_PCIE_TX_POWER_CTRL_1`.

## State And Persistence
State is stored in NBIO, GDC/PCIe port, and MMIO remap registers. It is reset-scoped and not persisted.

## Dependencies And Integration Points
It depends on generated NBIO 7.2 headers, local register aliases for related IPs, KFD remap constants, and common SOC15 NBIO calls.

## Risks
The file multiplexes several IP versions with local register definitions, so adding another NBIO minor version requires careful switch updates. Doorbell callbacks ignore the instance argument for SDMA/VCN in this implementation, which is correct only for the covered layout.

## Test Signals
Signals include correct revision ID on Yellow Carp-style parts, MC access enablement, SDMA/VCN/IH doorbell progress, clock/light-sleep flag transitions, and reset behavior after strap clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.h

## Purpose
`nbio_v7_2.h` exposes NBIO 7.2 flush and function tables.

## Important APIs, Types, And Functions
It declares `nbio_v7_2_hdp_flush_reg` and `nbio_v7_2_funcs`.

## Control Flow
No runtime behavior exists. ASIC selection uses the declarations to install the NBIO 7.2 implementation.

## State And Persistence
The header has no state. The actual constant tables are in `nbio_v7_2.c`.

## Dependencies And Integration Points
It depends on `soc15_common.h` and the shared NBIO callback ABI.

## Risks
The header does not communicate the IP-version-specific behavior inside the C file; consumers must select it only for compatible hardware.

## Test Signals
Compile/link success and matching hardware reaching common init with `nbio_v7_2_funcs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c

## Purpose
`nbio_v7_4.c` implements NBIO 7.4 support for Arcturus/Aldebaran-class devices. It includes doorbell setup for many SDMA instances, VCN doorbells with Aldebaran offset variants, HDP flush mapping, BIF light sleep, ASPM/LTR programming, BACO dummy-mode cleanup, doorbell interrupt control, and the most complete RAS controller/ATHUB handling in this subset.

## Important APIs, Types, And Functions
Exports are `nbio_v7_4_hdp_flush_reg`, `nbio_v7_4_funcs`, `nbio_v7_4_ras_hw_ops`, and `nbio_v7_4_ras`. Key functions include `nbio_v7_4_sdma_doorbell_range()`, `vcn_doorbell_range()`, `handle_ras_controller_intr_no_bifring()`, `handle_ras_err_event_athub_intr_no_bifring()`, `query_ras_error_count()`, `enable_doorbell_interrupt()`, `program_aspm()`, and `set_reg_remap()`.

## Control Flow
Common init configures NBIO registers, clears BACO dummy enable for NBIO `7.4.4`, remaps HDP registers, and enables doorbells. SDMA doorbell register selection handles non-consecutive SDMA2-7 ranges and an Aldebaran SDMA4 offset. RAS initialization registers controller and ATHUB interrupt IDs; because the BIF ring is disabled, real handling polls doorbell interrupt status, clears it, updates RAS counters, emits logs, and calls the global RAS ISR.

## State And Persistence
The file updates NBIO, PCIe SMN, Aldebaran-specific BIF registers, RAS manager counters, and `adev->nbio` IRQ source descriptors. RAS error counts accumulate in kernel state, while hardware status is cleared after handling.

## Dependencies And Integration Points
It depends on generated NBIO 7.4 headers, local Aldebaran register aliases, `amdgpu_ras`, `amdgpu_irq_add_id()`, SOC15 BIF client IDs, PCIe ASPM support, and KFD remap constants.

## Risks
Aldebaran conditional paths are numerous and easy to regress. RAS status clearing and EOI writes are ordering-sensitive. Some code in this snapshot shows duplicated lines around the Aldebaran interrupt-control read, which should be compared against upstream before modifying.

## Test Signals
RAS injection/query tests, repeated ATHUB/controller interrupt clearing, SDMA0-7 doorbells, Aldebaran VCN/SDMA offset tests, BACO reset paths, ASPM behavior, and HDP flush validation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.h

## Purpose
`nbio_v7_4.h` declares NBIO 7.4 operation, flush, and RAS objects.

## Important APIs, Types, And Functions
It exposes `nbio_v7_4_hdp_flush_reg`, `nbio_v7_4_funcs`, and mutable `nbio_v7_4_ras`.

## Control Flow
No executable logic exists. Common ASIC code uses this header to bind NBIO callbacks and RAS behavior for NBIO 7.4 hardware.

## State And Persistence
The header owns no state, but it exposes a mutable RAS object defined by the C file.

## Dependencies And Integration Points
It depends on `soc15_common.h` and integrates with common NBIO and RAS setup.

## Risks
Because RAS is mutable global state, object definition and initialization order matter. Any mismatch with the C file breaks link or runtime RAS registration.

## Test Signals
Build/link success, plus runtime registration of `pcie_bif` RAS block and NBIO 7.4 callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c

## Purpose
`nbio_v7_7.c` supports NBIO 7.7 devices with BIF1/BIF0 split register naming. It supplies HDP remap, PF0 flush masks, BIF1 framebuffer and interrupt control, CSDMA/VCN/IH doorbells, PCIe port offsets, request-size initialization, clock/light-sleep gating, and remap selection.

## Important APIs, Types, And Functions
Exports are `nbio_v7_7_hdp_flush_reg` and `nbio_v7_7_funcs`. Important callbacks are `nbio_v7_7_sdma_doorbell_range()`, `vcn_doorbell_range()`, `ih_control()`, `init_registers()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `get_pcie_port_index_offset()`, and `set_reg_remap()`.

## Control Flow
Init sets BIF0 PCIe request-size controls and clears a strap bit for NBIO `7.7.0`. Doorbell callbacks use CSDMA and VCN0 GDC ranges, while IH writes the GDC0 IH range. Interrupt control uses BIF_BX1 registers. Clock gating writes BIF0 CPM control, and light sleep writes BIF0 PCIE_CNTL2 plus TX_POWER_CTRL_1.

## State And Persistence
State is volatile in NBIO/BIF/GDC registers and `adev->rmmio_remap`. Self-ring aperture uses PF0 doorbell GPA base registers.

## Dependencies And Integration Points
It depends on generated NBIO 7.7 headers, SOC15 register helpers, KFD remap constants, and common NBIO dispatch.

## Risks
The header declares `nbio_v7_7_ras_funcs`, but this C file does not define RAS functions in the snapshot. BIF0/BIF1 split use makes register selection error-prone. The SDMA callback uses a single CSDMA doorbell range, so it is not a generic multi-instance SDMA implementation.

## Test Signals
Test CSDMA, VCN, and IH doorbells; BIF1 interrupt dummy-read setup; clock/light-sleep flags; NBIO `7.7.0` reset strap behavior; and link-time behavior around RAS declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.h

## Purpose
`nbio_v7_7.h` declares NBIO 7.7 public objects.

## Important APIs, Types, And Functions
It declares `nbio_v7_7_hdp_flush_reg`, `nbio_v7_7_funcs`, and `nbio_v7_7_ras_funcs`.

## Control Flow
There is no runtime logic. ASIC dispatch includes it for NBIO 7.7 table selection.

## State And Persistence
No state is held in the header.

## Dependencies And Integration Points
It depends on `soc15_common.h`; intended integration is the common NBIO/RAS framework.

## Risks
`nbio_v7_7_ras_funcs` is declared but not defined in `nbio_v7_7.c` in this source set, so usage must be verified against the broader tree or treated as stale.

## Test Signals
Compile/link with all NBIO 7.7 consumers enabled is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c

## Purpose
`nbio_v7_9.c` implements a multi-AID NBIO 7.9 backend for newer datacenter parts. Beyond standard NBIO services, it routes SDMA and VCN doorbells through per-AID S2A entries, exposes compute and memory partition mode queries, detects NPS switch requests, manages XCC doorbell fences, clears BACO dummy state per AID, controls doorbell interrupt masking, and registers RAS controller/ATHUB handlers.

## Important APIs, Types, And Functions
Exports are `nbio_v7_9_hdp_flush_reg`, `nbio_v7_9_funcs`, `nbio_v7_9_ras_hw_ops`, and `nbio_v7_9_ras`. Key functions include `sdma_doorbell_range()`, `vcn_doorbell_range()`, `get_compute_partition_mode()`, `get_memory_partition_mode()`, `is_nps_switch_requested()`, `init_registers()`, `enable_doorbell_interrupt()`, and the RAS no-BIF-ring handlers.

## Control Flow
SDMA doorbell setup maps the SDMA device instance to an AID and per-AID instance slot, then writes both range entries and S2A port control with distinct AWID/range/address values. VCN doorbells choose range size by GC IP and add a fence bit for nonzero AIDs. Init programs XCC doorbell fences, GFX interrupt monitor masks, per-AID SHUB slave-mode fences, and clears BACO dummy enable when not in SR-IOV. Partition queries read NBIO partition status/capability registers.

## State And Persistence
State spans per-AID NBIO extended registers, `adev->sdma.instance[].aid_id`, `adev->aid_mask`, `adev->gfx.xcc_mask`, partition status registers, and RAS manager counters. It is hardware/runtime state, not persistent storage.

## Dependencies And Integration Points
It depends on generated NBIO 7.9 headers, BIF interrupt IDs, `amdgpu_ras`, SDMA instance metadata, XCC/AID topology helpers, KFD remap constants, and common NBIO dispatch.

## Risks
Multi-AID routing depends on correct topology metadata; wrong `aid_id` or `num_inst_per_aid` sends doorbells to the wrong engine. Clock-gating callbacks are intentionally empty. `query_ras_error_count()` is empty, so RAS controller interrupts log but cannot harvest counts. The snapshot includes duplicated text in the doorbell aperture write, which should be checked before editing.

## Test Signals
Exercise SDMA instances across AIDs, VCN on multiple AIDs, XCC doorbell fences, partition mode sysfs/ioctl consumers, NPS switch status, RAS interrupt registration/clear paths, and BACO dummy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.h

## Purpose
`nbio_v7_9.h` declares the NBIO 7.9 operation, flush, and RAS objects.

## Important APIs, Types, And Functions
It exposes `nbio_v7_9_hdp_flush_reg`, `nbio_v7_9_funcs`, and mutable `nbio_v7_9_ras`.

## Control Flow
No executable control flow exists. Device setup includes the header and selects the exported tables for NBIO 7.9 hardware.

## State And Persistence
The header owns no state; the C file defines the mutable RAS object and constant tables.

## Dependencies And Integration Points
It depends on `soc15_common.h` and the common AMDGPU NBIO/RAS interfaces.

## Risks
The RAS object is mutable and includes callbacks whose implementation is partial for error-count harvest, so consumers need runtime capability awareness.

## Test Signals
Build/link success and runtime registration of NBIO 7.9 funcs/RAS block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c

## Purpose
`nv.c` is the Navi/common IP block implementation for AMDGPU. It binds ASIC callbacks, video codec capability tables, register-read allowlists, reset method selection, doorbell index assignment, virtualization setup, common early/late/software/hardware init, suspend/resume, clockgating control, and NBIO/HDP/SMUIO integration.

## Important APIs, Types, And Functions
Exports are `nv_common_ip_block`, `nv_grbm_select()`, and `nv_set_virt_ops()`. Important internal surfaces include `nv_query_video_codecs()`, `nv_read_register()`, `nv_asic_reset_method()`, `nv_asic_reset()`, `nv_init_doorbell_index()`, `nv_update_umd_stable_pstate()`, `nv_asic_funcs`, and the `nv_common_ip_funcs` lifecycle table. Codec tables cover Navi, Sienna Cichlid, SR-IOV Sienna Cichlid, Beige Goby, and Yellow Carp.

## Control Flow
`nv_common_early_init()` first calls the already-selected NBIO `set_reg_remap()`, wires indirect PCIe and DIDT register accessors, installs `nv_asic_funcs`, reads revision IDs, and chooses CG/PG flags plus external revision IDs by GC IP version. It initializes SR-IOV settings when needed. Later init gets mailbox IRQs, updates SR-IOV video codec tables, and enables self-ring doorbells. Hardware init applies NBIO workarounds, programs ASPM, initializes NBIO registers, remaps HDP flush registers when allowed, and enables doorbell aperture. Suspend/fini disables doorbell apertures.

## State And Persistence
The file mutates `adev` extensively: ASIC funcs, register accessor tables, revision IDs, CG/PG flags, doorbell indices, virtualization IRQ state, codec tables for SR-IOV, and stable-pstate behavior. All state is runtime kernel/device state.

## Dependencies And Integration Points
It depends on AMDGPU core, atom BIOS, IH, UVD/VCE/VCN/JPEG/GFX/SDMA/HDP/GMC/MMHUB/SMUIO blocks, NBIO version tables, PSP/DPM reset services, PCI reset, SR-IOV mailbox support, and DRM video capability reporting.

## Risks
GC IP switch coverage controls whether the common block probes at all; missing an IP returns `-EINVAL`. Reset method choice depends on MP1 IP and global module parameters. Codec capabilities are table-driven and can diverge between bare metal and SR-IOV. Stable pstate toggles RLC safe mode and ASPM, so ordering matters. The source snapshot shows duplicated code in the SR-IOV codec branch and duplicate MP1 switch case labels, both worth comparing to upstream.

## Test Signals
Signals include successful common IP probe across supported GC IPs, correct external revision IDs, codec query ioctls, reset method logs and recovery, SR-IOV mailbox/video capability updates, KFD/HDP remap, doorbell index correctness, and clockgating flags from NBIO/HDP/SMUIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.h

## Purpose
`nv.h` declares the Navi common IP block and the few cross-file helper entry points exported by `nv.c`.

## Important APIs, Types, And Functions
It includes `nbio_v2_3.h`, declares `nv_common_ip_block`, `nv_grbm_select()`, `nv_set_virt_ops()`, and `cyan_skillfish_reg_base_init()`.

## Control Flow
There is no header control flow. Other AMDGPU files include it to install `nv_common_ip_block`, select GRBM queues through `nv_grbm_select()`, initialize virtualization ops, or call Cyan Skillfish register-base setup.

## State And Persistence
No state is defined in the header. The declared functions mutate `adev` state in their implementations.

## Dependencies And Integration Points
It depends on the NBIO 2.3 header and AMDGPU device type definitions from included contexts. `cyan_skillfish_reg_base_init()` is declared here for a platform-specific integration point outside this source pair.

## Risks
The direct include of `nbio_v2_3.h` reflects Navi baseline assumptions; other NBIO versions are included by implementation files. A declaration without a local definition, such as `cyan_skillfish_reg_base_init()`, requires link coverage in the wider tree.

## Test Signals
Compile/link success, common IP block registration, GRBM queue selection behavior, SR-IOV virt ops installation, and Cyan Skillfish builds are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.h -->
