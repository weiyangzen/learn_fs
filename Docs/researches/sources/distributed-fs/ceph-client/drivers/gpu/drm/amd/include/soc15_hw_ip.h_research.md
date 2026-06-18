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
