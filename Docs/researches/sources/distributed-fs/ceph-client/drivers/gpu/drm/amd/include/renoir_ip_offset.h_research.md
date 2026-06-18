# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/renoir_ip_offset.h

## Purpose

`renoir_ip_offset.h` is the generated AMDGPU IP base-offset map for Renoir APU/DCN 2.1 hardware. It supplies compile-time MMIO base addresses for display, multimedia, management, bus, audio, USB, memory-controller, and related blocks. Consumers use these constants to compose correct register addresses for Renoir-specific driver paths.

The header uses `_renoir_ip_offset_HEADER`, `MAX_INSTANCE` 7, and `MAX_SEGMENT` 5. It follows the same `IP_BASE` table plus flattened macro pattern used by other AMDGPU ASIC offset headers, but its block list is broader than Navi 10 because Renoir is an APU-oriented map.

## Important APIs, Types, And Data

The exported generated types are:

- `struct IP_BASE_INSTANCE`, containing five segment entries.
- `struct IP_BASE`, containing seven instances and marked `__maybe_unused`.

Static base tables include `ACP_BASE`, `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO0_BASE`, `DF_BASE`, `DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDA_BASE`, `HDP_BASE`, `IOHC0_BASE`, `ISP_BASE`, `L2IMU0_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `DCN_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA0_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB0_BASE`, and `UVD0_BASE`.

The flattened macro set follows `BLOCK_BASE__INSTn_SEGm` through the declared seven-by-five matrix. Notable populated areas include APU peripherals (`ACP_BASE`, `HDA_BASE`, `USB0_BASE`, `ISP_BASE`), display blocks (`DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `DCN_BASE`), management processor windows (`MP0_BASE`, `MP1_BASE`), IO fabric (`IOHC0_BASE`, `L2IMU0_BASE`, `NBIF0_BASE`, `PCIE0_BASE`), and two populated `UMC_BASE` instances.

## Control Flow

This file has no functions or runtime branches. Its operational flow is:

1. Renoir-specific display or DMUB code includes the header.
2. The code references base tables or flattened macros while building register addresses.
3. Register helpers add the base to block-relative offsets from matching register headers.
4. The driver programs display clocks, GPIO, IRQs, DMUB/DCN resources, VBIOS SMU access, or other hardware state.

Direct includes found in this tree include `display/dmub/src/dmub_dcn21.c`, `display/dc/resource/dcn21/dcn21_resource.c`, `display/dc/gpio/dcn21/hw_factory_dcn21.c`, `display/dc/gpio/dcn21/hw_translate_dcn21.c`, `display/dc/irq/dcn21/irq_service_dcn21.c`, `display/dc/clk_mgr/dcn21/rn_clk_mgr.c`, and `display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c`.

## State And Persistence Behavior

The header contributes immutable constants only. It owns no dynamic state and performs no persistence. The stateful consequences occur through consumers that program hardware registers using these bases: display resources, GPIO/DDC lines, IRQ routing, clock manager state, DMUB interactions, SMU/VBIOS mailbox access, audio/USB/ACP/ISP-related registers, and memory/bus diagnostics can all depend on correct offsets.

The compiled constants persist for the lifetime of the loaded driver and define the Renoir hardware address contract for those consumers.

## Dependencies

The syntactic dependency is `__maybe_unused`. Operational dependencies are AMDGPU DCN 2.1 and DMUB code, SOC15-style register helpers, generation-matched register offset/mask headers, and ASIC detection that selects Renoir paths only for compatible devices.

Because this header defines generic symbols such as `CLK_BASE`, `MP0_BASE`, and `struct IP_BASE`, translation units should avoid including multiple ASIC IP-offset headers together unless names are isolated.

## Integration Points

The strongest integration points are DCN 2.1 resource construction, GPIO factory/translation, IRQ service setup, Renoir clock manager code, VBIOS SMU access, and DMUB support. `DCN_BASE`, `DMU_BASE`, `DPCS_BASE`, `DIO_BASE`, `CLK_BASE`, `MP0_BASE`, `MP1_BASE`, `SMUIO_BASE`, and `THM_BASE` are directly relevant to display bring-up and power/clock control. APU-specific tables such as `ACP_BASE`, `HDA_BASE`, `USB0_BASE`, and `ISP_BASE` reflect integration with non-discrete GPU peripherals.

The file also aligns with sibling generated maps such as `navi12_ip_offset.h` and `navi14_ip_offset.h`, but Renoir has distinct low and high fabric/peripheral segments that should not be substituted across ASICs.

## Risks

Incorrect Renoir base offsets can break core user-visible display behavior. Bad display bases can cause modeset, GPIO/DDC, hotplug, IRQ, or DMUB failures. Bad `MP0_BASE`/`MP1_BASE` values can break SMU or firmware mailbox access. Bad APU peripheral bases can affect audio, USB, ACP, or ISP-related paths if consumers use those entries.

The file includes both `DCN_BASE` and display-adjacent `DMU_BASE`/`DPCS_BASE` tables with overlapping-looking segment values. Consumers must choose the intended block constant; using a similarly named table from another generation can compile but target the wrong address. Zero placeholders remain a risk for code that treats nonzero as the only validity criterion without understanding the table.

## Test Signals

Useful validation starts with compile coverage of DCN 2.1, Renoir clock manager, DMUB, GPIO, and IRQ consumers. Hardware signals include Renoir probe, display modeset on internal and external connectors, HPD/DDC behavior, DMUB initialization, clock manager and VBIOS SMU operations, suspend/resume, audio-over-display behavior, and no timeouts while polling display, SMU, or interrupt status registers.

Register dump comparison against expected Renoir addresses for `DCN_BASE`, `CLK_BASE`, `MP0_BASE`, `MP1_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and bus/peripheral tables is the most direct check that the map matches hardware.
