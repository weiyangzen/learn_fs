# Research: subset-b-003495

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/sienna_cichlid_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/sienna_cichlid_ip_offset.h

## Purpose

`sienna_cichlid_ip_offset.h` is a generated-style AMDGPU/DC register-base map for the Sienna Cichlid ASIC family. It gives consumers two equivalent ways to reach hardware block base addresses:

- typed static tables, `static const struct IP_BASE <BLOCK>_BASE`, indexed as instance then segment;
- preprocessor constants named `<BLOCK>_BASE__INST<n>_SEG<m>`, usable inside register-list macros.

The file is not executable logic. Its job is to make register address construction deterministic for display, DMUB, GPIO, IRQ, clock manager, and related DCN 3.0 code that combines a block base with generated register offsets such as `mm...` and `..._BASE_IDX`.

## Important APIs, Types, And Constants

- `MAX_INSTANCE` is `7`; every `IP_BASE` table contains seven instance rows.
- `MAX_SEGMENT` is `5`; every instance row contains five segment slots.
- `struct IP_BASE_INSTANCE` wraps `unsigned int segment[MAX_SEGMENT]`.
- `struct IP_BASE` wraps `struct IP_BASE_INSTANCE instance[MAX_INSTANCE]` and is annotated `__maybe_unused`, which is useful because inclusion sites often consume only macro constants.
- Static block tables are provided for `ATHUB`, `CLK`, `DF`, `DIO`, `DCN`, `DPCS`, `FUSE`, `GC`, `HDA`, `HDP`, `MMHUB`, `MP0`, `MP1`, `NBIO`, `OSSSYS`, `PCIE0`, `SDMA0`, `SDMA1`, `SMUIO`, `THM`, `UMC`, `USB0`, and `VCN`.
- The macro matrix covers the same block names for all seven instances and five segments, yielding 805 `<BLOCK>_BASE__INST<n>_SEG<m>` definitions.

Notable populated ranges include multi-segment DCN/DPCS display bases, five-segment MP0/MP1/NBIO/PCIE0 bases, seven UMC instance rows, seven CLK instance rows, and two populated VCN instance rows. Zero values are meaningful sentinels for absent instances or absent segment slots, not dynamically discovered data.

## Control Flow And Data Flow

There is no function-level control flow. At compile time, include sites expand `BASE_INNER(seg)` or similar macros into constants such as `DCN_BASE__INST0_SEG4`; then generated register macros add generated register offsets:

- `BASE(mmREG_BASE_IDX) + mmREG` in DCN display code;
- static register tables, for example clock-manager register initializers, storing absolute SOC15-style register offsets;
- GPIO translation switch cases matching the same computed offsets.

Where the static `IP_BASE` tables are used, consumers can assign `adev->reg_offset[<HWIP>][instance]` to the address of a table instance, then later index `[base_idx]` while constructing register accesses. This repo shows that pattern in neighboring ASIC offset headers and AMGPU register-init paths, while Sienna Cichlid include sites in this checkout are primarily DC display and DMUB files that include the header directly and use the macro constants.

## State And Persistence Behavior

The file stores immutable compile-time constants only. It does not allocate memory, mutate driver state, persist device state, or read hardware. Its values become part of compiled driver code and indirectly influence runtime register access addresses. The only "state" is the static read-only data emitted into each translation unit that references the tables or macros.

## Dependencies

- Depends on a kernel build environment that defines `__maybe_unused`; the header itself does not include the defining header.
- Must match generated block register headers such as `dcn/dcn_3_0_0_offset.h`, `dpcs/dpcs_3_0_0_offset.h`, `mmhub/mmhub_2_0_0_offset.h`, and `nbio/nbio_7_4_offset.h`, because their `_BASE_IDX` values select segment indexes from this file.
- Included by DCN/DMUB Sienna Cichlid paths including `display/dmub/src/dmub_dcn30.c`, `display/dmub/src/dmub_dcn303.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn303/irq_service_dcn303.c`, `display/dc/gpio/dcn30/hw_translate_dcn30.c`, `display/dc/gpio/dcn30/hw_factory_dcn30.c`, `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/resource/dcn303/dcn303_resource.c`, and `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`.
- Conceptually depends on AMDGPU hardware-IP identifiers from `soc15_hw_ip.h` when table-based offsets are attached to `adev->reg_offset[HWIP][instance]`.

## Integration Points

The main integration point is address construction for register reads/writes in AMD display and graphics code. For example, DCN code defines `BASE_INNER(seg) DCN_BASE__INST0_SEG ## seg`, then defines `REG(reg_name)` as `BASE(mm ## reg_name ## _BASE_IDX) + mm ## reg_name`. This makes the generated register offset headers hardware-family-specific without changing each register user.

The static tables align with `struct amdgpu_device::reg_offset[MAX_HWIP][HWIP_MAX_INSTANCE]`, whose entries are later consumed by SOC15 register helpers in `amdgpu/soc15_common.h`. The exact block names must therefore stay consistent with HWIP names and register base-index macros.

## Risks And Edge Cases

- Wrong segment values cause silent register misaddressing: reads and writes compile and run but target the wrong MMIO location.
- The `MAX_SEGMENT` width must be compatible with every `_BASE_IDX` used by included generated register headers. A new base index above 4 would become an out-of-bounds table access in table consumers or an undefined macro in macro consumers.
- Zero is overloaded as a valid base for some hardware ranges and as "not present" for most unused instance/segment cells. Consumers cannot infer presence from nonzero alone unless the relevant block's address map makes zero impossible.
- The struct names `IP_BASE_INSTANCE` and `IP_BASE` are generic and repeated by other generated offset headers. Include ordering must avoid including two incompatible generated offset headers with the same guard-disabled type names in one translation unit.
- Since the static tables live in a header, any non-`static` conversion would create multiple-definition link errors. Keeping them `static const` is required for header inclusion.

## Test Signals

- Build coverage from all DCN/DMUB translation units that include this header is the first signal: missing macros, bad type definitions, or conflicting generated headers fail compilation.
- Runtime display smoke tests are important: modeset, HPD, GPIO, clock manager, IRQ, and DMUB initialization paths exercise the computed register addresses.
- Register access tracing or debugfs reads can validate that DCN, DPCS, MMHUB, NBIO, and SMUIO addresses match Sienna Cichlid hardware documentation.
- Regression signals include blank display, hotplug failure, interrupt storms or missing vblank/pageflip interrupts, SMU/clock-manager failures, and GPU hangs during display bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/sienna_cichlid_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_hw_ip.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_hw_ip.h

## Purpose

`soc15_hw_ip.h` defines numeric hardware IP IDs used by SOC15-era and later AMDGPU discovery, versioning, register-offset, firmware, reset, and error-reporting paths. These IDs are hardware-facing identifiers, not driver-local enum ordinals. Driver code uses them to classify blocks such as graphics, memory hubs, SDMA, PSP/SMU management processors, display, PCIe/NBIO, UMC, USB, and XGMI.

## Important APIs, Types, And Constants

This header exports preprocessor constants only. Important definitions include:

- management and system blocks: `MP0_HWID` `255`, `MP1_HWID` `1`, `MP2_HWID` `2`, `SMUIO_HWID` `4`, `FUSE_HWID` `5`, `THM_HWID` `3`, `PWR_HWID` `10`;
- graphics/display/media blocks: `GC_HWID` `11`, `UVD_HWID` `12`, `VCN_HWID` as an alias of `UVD_HWID`, `AUDIO_AZ_HWID` `13`, `DCO_HWID` `16`, `DIO_HWID` `272`, `VCE_HWID` `32`, `VPE_HWID` `21`;
- memory and fabric blocks: `MMHUB_HWID` `34`, `ATHUB_HWID` `35`, `DF_HWID` `46`, `UMC_HWID` `150`, `XGMI_HWID` `200`;
- DMA and I/O blocks: `SDMA0_HWID` `42`, `SDMA1_HWID` `43`, `SDMA2_HWID` `68`, `SDMA3_HWID` `69`, `PCIE_HWID` `70`, `NBIF_HWID` `108`, `USB_HWID` `170`, `SATA_HWID` `168`;
- debug and miscellaneous IDs such as `DBGU_NBIO_HWID`, `DBGU0_HWID`, `DBGU1_HWID`, `OSSSYS_HWID`, `HDP_HWID`, `ISP_HWID`, `FCH_HWID`, `ATU_HWID`, and `AIGC_HWID`.

There are no functions or structs. The exported names are stable compile-time identifiers.

## Control Flow And Data Flow

There is no direct control flow. Data flow is through constant substitution into arrays, switch statements, IP discovery maps, firmware selection, diagnostics, and register-offset selection. The broader AMDGPU code maps discovery-table hardware IDs to driver HWIP indexes, stores IP versions under `adev->ip_versions[MAX_HWIP][HWIP_MAX_INSTANCE]`, and uses driver HWIP indexes such as `GC_HWIP`, `MMHUB_HWIP`, and `MP0_HWIP` to query `amdgpu_ip_version()` and select code paths.

Although this header defines `*_HWID` values rather than `*_HWIP` driver indexes, the two namespaces are tightly linked by discovery and mapping code. A hardware ID discovered from firmware tables must map to the correct driver IP block, otherwise version-dependent code will make decisions for the wrong block.

## State And Persistence Behavior

The header has no runtime state and no persistence. Its constants become compiled-in ABI knowledge. The persistent aspect is external: firmware discovery tables, hardware register maps, dumps, and logs use these numeric IDs as contract values.

## Dependencies

- Included by AMDGPU discovery and hardware-management code that interprets SOC15 IP discovery tables.
- Must remain consistent with firmware or hardware discovery data; changing a number to match a local naming preference would break identification.
- Works with driver-local HWIP indexes and limits declared elsewhere, such as `MAX_HWIP`, `HWIP_MAX_INSTANCE`, `amdgpu_device::ip_versions`, and `amdgpu_device::reg_offset`.
- Complements ASIC offset headers like `sienna_cichlid_ip_offset.h`, because discovered/selected hardware blocks later require the right register-base tables.

## Integration Points

Common integration patterns include:

- IP-version branching such as graphics, PSP, GMC, SMU, XGMI, and VM code querying `amdgpu_ip_version(adev, GC_HWIP, 0)`, `amdgpu_ip_version(adev, MP0_HWIP, 0)`, or `amdgpu_ip_version(adev, MMHUB_HWIP, 0)` after discovery has mapped hardware IDs into driver state.
- Firmware naming and loading paths using decoded IP versions to select microcode files.
- Device coredump and debug output that iterate hardware IP indexes and print block names.
- Register helpers and generated offset maps that require a stable connection between hardware discovery IDs and driver HWIP slots.

## Risks And Edge Cases

- Numeric constants are hardware ABI values. Accidental renumbering can make the driver identify blocks incorrectly while still compiling cleanly.
- Aliases are intentional: `VCN_HWID` equals `UVD_HWID`, preserving historical naming for video decode/encode blocks. Code that assumes unique IDs for every name can misreport or double-count media IP.
- Some values are outside a compact 8-bit range, for example `DMU_HWID` `271`, `DIO_HWID` `272`, `DAZ_HWID` `274`, `ATU_HWID` `294`, and `AIGC_HWID` `295`. Any storage, parsing, or debug tooling that truncates hardware IDs to `u8` will corrupt these blocks.
- Adding a new `*_HWID` without updating discovery maps, name tables, register offset maps, and version handling leaves the constant unused or misclassified.

## Test Signals

- Compile coverage catches missing macro names but not semantic renumbering.
- Hardware discovery logs should show expected IP blocks and versions for SOC15/Navi/Sienna Cichlid class devices.
- Firmware loading tests should select expected files for PSP, graphics, SDMA, VCN, and related IPs.
- Runtime signals include successful GPU initialization, coredump hardware-IP naming, IP-version-specific feature selection, and absence of "unknown IP" discovery warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_hw_ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_ih_clientid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_ih_clientid.h

## Purpose

`soc15_ih_clientid.h` defines interrupt-handler client IDs for SOC15/Vega10+ hardware and for SOC21 hardware. These IDs identify which hardware client generated an interrupt vector. AMDGPU interrupt registration and dispatch use the IDs with source IDs to route interrupts to the correct `amdgpu_irq_src` handler.

## Important APIs, Types, And Constants

- `enum soc15_ih_clientid` covers base Vega10+ client IDs from `SOC15_IH_CLIENTID_IH = 0x00` through `SOC15_IH_CLIENTID_MP1 = 0x1f`, followed by `SOC15_IH_CLIENTID_MAX`.
- SOC15 aliases after `SOC15_IH_CLIENTID_MAX` express hardware naming reuse:
  - `SOC15_IH_CLIENTID_VCN = SOC15_IH_CLIENTID_UVD`;
  - `SOC15_IH_CLIENTID_VCN1 = SOC15_IH_CLIENTID_UVD1`;
  - `SOC15_IH_CLIENTID_SDMA2 = SOC15_IH_CLIENTID_ACP`;
  - `SOC15_IH_CLIENTID_SDMA3 = SOC15_IH_CLIENTID_DCE`;
  - `SOC15_IH_CLIENTID_SDMA3_Sienna_Cichlid = SOC15_IH_CLIENTID_ISP`;
  - `SOC15_IH_CLIENTID_SDMA4 = SOC15_IH_CLIENTID_ISP`;
  - `SOC15_IH_CLIENTID_SDMA5 = SOC15_IH_CLIENTID_VCE0`;
  - `SOC15_IH_CLIENTID_SDMA6 = SOC15_IH_CLIENTID_XDMA`;
  - `SOC15_IH_CLIENTID_SDMA7 = SOC15_IH_CLIENTID_VCE1`;
  - `SOC15_IH_CLIENTID_VMC1 = SOC15_IH_CLIENTID_PCIE0`.
- `extern const char *soc15_ih_clientid_name[];` declares the debug-name table implemented in `amdgpu/amdgpu_irq.c`.
- `enum soc21_ih_clientid` defines a smaller SOC21-specific ID set with names such as `SOC21_IH_CLIENTID_DCN`, `SOC21_IH_CLIENTID_GFX`, `SOC21_IH_CLIENTID_IMU`, `SOC21_IH_CLIENTID_VPE`, `SOC21_IH_CLIENTID_LSDMA`, `SOC21_IH_CLIENTID_MP0`, and `SOC21_IH_CLIENTID_MP1`.

## Control Flow And Data Flow

The header itself has no functions. At runtime, IH ring decoding populates `struct amdgpu_iv_entry::client_id` and `src_id`. The interrupt dispatch path checks `client_id` against `AMDGPU_IRQ_CLIENTID_MAX`, which is defined as `SOC15_IH_CLIENTID_MAX` in `amdgpu_irq.h`, and then indexes `adev->irq.client[client_id].sources[src_id]`. IP blocks register handlers with calls such as `amdgpu_irq_add_id(adev, SOC15_IH_CLIENTID_VCN, src_id, source)` or SOC21 equivalents.

The name table in `amdgpu_irq.c` mirrors the base SOC15 enum order and is used in diagnostics such as VM fault messages. The comment in this header explicitly warns that updates to the enum must also update that name table.

## State And Persistence Behavior

The enums define compiled-in interrupt ABI values. Runtime state lives outside this header:

- decoded IV entries carry the numeric `client_id`;
- `adev->irq.client[]` stores registered handler arrays by client ID;
- `soc15_ih_clientid_name[]` provides read-only diagnostic labels.

No data is persisted by this header, but the numeric values must match hardware interrupt vector encodings.

## Dependencies

- Included by `amdgpu_irq.h`, which sets `AMDGPU_IRQ_CLIENTID_MAX` to `SOC15_IH_CLIENTID_MAX` and sizes `struct amdgpu_irq::client`.
- Implemented name dependency in `amdgpu_irq.c`; enum ordering and table ordering must stay synchronized.
- Used by IH implementations and IP blocks including VCN/JPEG, GMC, GFX, SDMA, NBIF, and virtualization paths when registering or decoding interrupts.
- SOC21 constants are consumed by newer IP code even though `AMDGPU_IRQ_CLIENTID_MAX` remains tied to the SOC15 max value; the SOC21 IDs still fit in the same 0x00-0x1f range represented by the SOC15 max.

## Integration Points

Primary integration is AMDGPU IRQ registration and dispatch:

- `amdgpu_irq_add_id()` registers a source handler under a `(client_id, src_id)` tuple.
- `amdgpu_irq_dispatch()` decodes an interrupt vector, validates the client and source IDs, handles legacy/ISP virtual IRQ shortcuts, and invokes the registered source callback.
- GMC VM fault code uses `entry->client_id` to classify fault source hubs and log readable client names.
- SDMA code maps engine instances to SOC15 client aliases, including Sienna Cichlid-specific SDMA3 behavior.

## Risks And Edge Cases

- Enum order is ABI-sensitive. Reordering base SOC15 entries breaks `soc15_ih_clientid_name[]`, handler registration arrays, and interrupt dispatch.
- Aliases mean several logical IP names share the same numeric client ID. Dispatch code cannot distinguish them by client ID alone; it must also use source ID, ASIC version, or engine instance context.
- `SOC15_IH_CLIENTID_MAX` is placed before aliases. This is intentional for array sizing; moving aliases before `MAX` would increase `AMDGPU_IRQ_CLIENTID_MAX` and could alter table expectations.
- SOC21 has sparse values with no entries for some SOC15 clients. Code shared between SOC15 and SOC21 must not blindly print SOC21 client IDs through the SOC15 name table unless the name collision is acceptable.
- The special case in interrupt dispatch for `SOC15_IH_CLIENTID_ISP` means aliases that equal ISP, such as SDMA3 Sienna Cichlid or SDMA4, can follow the virtual IRQ path under some conditions.

## Test Signals

- Compile coverage catches missing enum names in IP blocks.
- IRQ registration logs and runtime interrupt handling should show no "Invalid client_id", "Unregistered interrupt client_id", or "Unregistered interrupt src_id" messages for supported hardware.
- VCN/JPEG, SDMA, GFX, GMC VM fault, hotplug/vblank, and PSP/SMU interrupt paths are useful runtime smoke tests because they register and dispatch different client IDs.
- Fault injection or debug traces that decode IH vectors can validate that `soc15_ih_clientid_name[]` labels match the numeric client IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_ih_clientid.h -->
