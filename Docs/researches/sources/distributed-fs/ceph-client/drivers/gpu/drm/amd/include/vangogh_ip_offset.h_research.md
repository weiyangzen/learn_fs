# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vangogh_ip_offset.h

## Purpose
This generated-style AMDGPU header describes the Vangogh ASIC register base address map by hardware IP block, instance, and segment. It lets Vangogh display, clock, SMU, DMUB, and resource code resolve generated register offsets such as `mmMP1_SMN_C2PMSG_91` or DCN register offsets into actual MMIO addresses by adding the correct per-block base segment.

The file is data-only. It does not implement device logic, but incorrect values here directly affect where the driver reads and writes GPU registers.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as `8` and `MAX_SEGMENT` as `6`. `struct IP_BASE_INSTANCE` stores six `unsigned int segment[]` offsets, and `struct IP_BASE` stores eight instances. The `IP_BASE` type is marked `__maybe_unused` so including translation units can use either table objects or flattened macros without warning churn.

The static `IP_BASE` tables cover Vangogh IP blocks:

- `ACP_BASE`, `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DCN_BASE`, `DPCS_BASE`, `FCH_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `ISP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `MP2_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB_BASE`, and `VCN_BASE`.
- Most blocks populate only instance 0 and leave the remaining instance slots zeroed.
- Multi-instance tables include `CLK_BASE` instances 0-7, `UMC_BASE` instances 0-3, `USB_BASE` instances 0-2, and `SMUIO_BASE` instances 0-1.
- `MP0_BASE` and `MP1_BASE` carry the same segment map: `0x00016000`, `0x0243FC00`, `0x00DC0000`, `0x00E00000`, `0x00E40000`, and `0`.
- `DCN_BASE` and `DPCS_BASE` share display base segments `0x00000012`, `0x000000C0`, `0x000034C0`, `0x00009000`, `0x02403C00`, and `0`.
- `NBIO_BASE` and `PCIE0_BASE` share segments including `0x00000000`, `0x00000014`, `0x00000D20`, `0x00010400`, `0x0241B000`, and `0x04040000`; segment 0 is a valid populated value for these blocks, not only an absent sentinel.

For every table entry the file also emits flattened preprocessor constants such as `CLK_BASE__INST0_SEG1`, `DCN_BASE__INST0_SEG4`, `MP1_BASE__INST0_SEG2`, `NBIO_BASE__INST0_SEG5`, and `VCN_BASE__INST7_SEG5`. These support macro-generated register lists that need compile-time token concatenation rather than indexing into `struct IP_BASE`.

## Control Flow
There are no functions and no local branching. Runtime control flow appears in include sites:

- `display/dc/clk_mgr/dcn301/dcn301_smu.c` includes this header and defines `REG(reg_name)` as `MP0_BASE.instance[0].segment[mm..._BASE_IDX] + mm...`. Its SMU message path waits on and writes MP1 C2PMSG registers through this computed address path.
- `display/dc/clk_mgr/dcn301/vg_clk_mgr.c` includes this header and computes clock register addresses from `CLK_BASE.instance[0].segment[mm..._BASE_IDX] + mm...` when updating Vangogh display clocks.
- `display/dmub/src/dmub_dcn301.c` includes this header, defines `BASE_INNER(seg)` as `DCN_BASE__INST0_SEG##seg`, and feeds `dmub_reg.h`'s `REG_OFFSET()` macro so DMUB common and DMCUB internal register tables are initialized with Vangogh DCN base segments.
- `display/dc/resource/dcn301/dcn301_resource.c` includes this header and uses flattened `DCN_BASE`, `NBIO_BASE`, `MMHUB_BASE`, and `CLK_BASE` macros to build static register offset tables for DCN 3.01 display resources.

The effective flow is: generated register header supplies a register-relative offset and `_BASE_IDX`; this file supplies the base segment for that index; local macros add them; higher-level display, SMU, DMUB, and resource helpers perform the register access.

## State And Persistence
All state in this header is immutable static compile-time data. It is compiled into any object that includes it, but it has no writable globals, no heap allocation, no firmware state, and no persistence behavior.

Runtime state is indirect: consumers store or embed computed register addresses in static register tables or use the base tables during reads and writes. The actual hardware state affected by those reads and writes lives in Vangogh MMIO registers and firmware mailboxes, not in this header.

## Dependencies
This header depends on kernel/compiler support for `__maybe_unused`; include sites in the AMDGPU display tree normally have the required Linux compiler annotations available through surrounding headers. It is tightly coupled to the generated Vangogh register offset headers whose `_BASE_IDX` values index these six segment slots, including:

- `mp/mp_11_5_0_offset.h` for SMU mailbox registers in `dcn301_smu.c`.
- `clk/clk_11_5_0_offset.h` for clock manager registers in `vg_clk_mgr.c`.
- `dcn/dcn_3_0_1_offset.h` and `dcn/dcn_3_0_1_sh_mask.h` for DMUB and DCN 3.01 display register tables.

The generic names `MAX_INSTANCE`, `MAX_SEGMENT`, `struct IP_BASE_INSTANCE`, `struct IP_BASE`, and table names like `CLK_BASE` are shared by many AMD ASIC offset headers. Translation units should include only the offset header that matches their ASIC path, or use local undef/isolated include patterns already present in the display tree.

## Integration Points
The main integration point is Vangogh display support in the AMDGPU DRM driver. Vangogh is identified elsewhere by ASIC revision and APU flags; once DCN 3.01/Vangogh paths are selected, this header supplies the address-map constants for:

- DCN and DPCS display register addressing.
- DMUB service register offset initialization.
- Display clock and SMU mailbox programming.
- NBIO/PCIE scratch and resource registers.
- MMHUB, GC, HDP, ATHUB, UMC, VCN, USB, ACP, FCH, ISP, thermal, fuse, and fabric base metadata for generated code that may reference those blocks.

This file is also aligned with sibling ASIC headers such as `sienna_cichlid_ip_offset.h`, `aldebaran_ip_offset.h`, and `beige_goby_ip_offset.h`; those files use the same table and macro pattern with ASIC-specific block coverage and segment values.

## Risks
Address-map errors are high impact. A wrong segment can make a normal register read or write target the wrong hardware block, producing display bring-up failures, SMU mailbox timeouts, corrupted clock programming, or hard-to-debug hangs.

Zero values need careful interpretation. Many zero entries are placeholders for absent instances or segments, but `NBIO_BASE__INST0_SEG0` and `PCIE0_BASE__INST0_SEG0` are valid zero base segments. Consumers must rely on generated `_BASE_IDX` contracts and block knowledge rather than treating every zero base as absent hardware.

The duplicated data forms can drift. Each base appears both in a `static const struct IP_BASE` initializer and in matching `#define ...__INST..._SEG...` constants. If one representation is edited without the other, table-based consumers and macro-based consumers can compute different addresses.

`MAX_INSTANCE` and `MAX_SEGMENT` are structural contracts. Reducing or increasing them without regenerating all table initializers and include-site assumptions can break builds or silently invalidate generated indexing.

Generic symbol names create include-order risk. Including another ASIC offset header in the same translation unit would redefine the same structs, limits, and base table identifiers.

## Test Signals
Useful compile-time signals are successful builds of `dcn301_smu.c`, `vg_clk_mgr.c`, `dmub_dcn301.c`, and `dcn301_resource.c`, because those exercise both the table form and flattened macro form.

Runtime signals should focus on Vangogh hardware or emulation paths:

- DMUB initialization succeeds and common/DMCUB register access does not fault.
- SMU mailbox operations in `dcn301_smu.c` return non-busy responses for messages such as get-SMU-version and display clock programming.
- Display clock transitions in `vg_clk_mgr.c` work across active-display, idle, and safe-to-lower paths.
- DCN 3.01 resource initialization can read stable NBIO scratch, MMHUB, CLK, and DCN registers using generated register tables.
- Suspend/resume and display hotplug are valuable integration tests because stale or wrong base segments often surface as SMU timeouts, blank display, or failed DMUB communication during mode-set transitions.
