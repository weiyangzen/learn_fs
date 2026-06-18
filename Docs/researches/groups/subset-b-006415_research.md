# subset-b-006415 research

Grouped research for the requested AMD ASoC ACP register and Pink Sardine driver files. Each section title preserves the source path and is wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_d.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_d.h

## Purpose
`acp_2_2_d.h` is a generated-style ACP 2.2 register address header. It exports only preprocessor constants named `mm...`, mapping ACP hardware register names to dword register offsets in the ACP 2.2 MMIO/register namespace. It is included by `sound/soc/amd/acp.h`, which is then consumed by the older ACP PCM/I2S DMA platform code. There are no functions, structs, or executable control paths in this file; its behavior is entirely defined by the numeric ABI it gives to MMIO access sites.

The file covers the ACP 2.2 hardware block at a broad level: 16 DMA channels, DMA descriptor tables and status, three DSP control/register windows, AXI-to-DAGB onion/garlic transport controls, DAGB page groups, ACP clock/reset/power/status registers, external and DSP interrupt registers, semaphores, SRBM client indexed access, firmware/timer/scratch registers, efuse and power FSM registers, voice wakeup registers, memory sleep/shutdown controls, and I2S speaker/microphone/Bluetooth controller registers.

## Important APIs, types, and constants
The exported API is the `mmACP_*` and `mmI2S_*` macro namespace. Major groups are:

- `mmACP_DMA_CNTL_0` through `mmACP_DMA_CNTL_15`, plus `mmACP_DMA_DSCR_STRT_IDX_*`, `mmACP_DMA_DSCR_CNT_*`, `mmACP_DMA_PRIO_*`, `mmACP_DMA_CUR_DSCR_*`, `mmACP_DMA_CUR_TRANS_CNT_*`, and `mmACP_DMA_ERR_STS_*`, define the per-channel DMA control/status register map.
- `mmACP_DMA_DESC_BASE_ADDR`, `mmACP_DMA_DESC_MAX_NUM_DSCR`, `mmACP_DMA_CH_STS`, and `mmACP_DMA_CH_GROUP` define global DMA descriptor and grouping registers.
- `mmACP_DSP{0,1,2}_CACHE_OFFSET*`, `CACHE_SIZE*`, `NONCACHE_OFFSET*`, `NONCACHE_SIZE*`, `DEBUG_PC`, `CLKRST_CNTL`, `RUNSTALL`, `WAIT_MODE`, `VECT_SEL`, and `DEBUG_REG*` define repeated register banks for three DSP instances.
- `mmACP_AXI2DAGB_ONION_*`, `mmACP_AXI2DAGB_GARLIC_*`, and `mmACP_DAGB_*` define data-fabric bridge setup, error status, counters, page size/base groups, and ATU control.
- `mmACP_CONTROL`, `mmACP_STATUS`, `mmACP_SOFT_RESET`, `mmACP_PwrMgmt_CNTL`, `mmACP_SMU_MAILBOX`, and `mmACP_PGFSM_*` define ACP-wide power, reset, status, and power-gating controls.
- `mmACP_EXTERNAL_INTR_*`, `mmACP_DSP_SW_INTR_*`, and `mmACP_DSP{0,1,2}_INTR_*` define host/DSP interrupt enable, status, ack, and timeout registers.
- `mmACP_I2SSP_*`, `mmACP_I2SMICSP_*`, and `mmACP_I2SBT_*` define the I2S speaker, mic/speaker, and Bluetooth banks.

This file intentionally does not expose typed helpers. Callers combine these offsets with bit masks from `acp_2_2_sh_mask.h` and local MMIO helpers such as `readl()`/`writel()`.

## Control flow
There is no runtime control flow. The effective control flow is at include/preprocessor time:

1. `sound/soc/amd/acp.h` includes this header.
2. ACP legacy platform code references the register-offset macros while programming DMA descriptors, I2S controllers, power tiles, reset, and counters.
3. The compiler substitutes the numeric offsets directly into MMIO access expressions.

The file therefore must be treated as a hardware contract, not as logic that can be refactored independently.

## State and persistence behavior
The header stores no software state. It names hardware state that persists in ACP registers while the device is powered. The registers named here include mutable state such as current DMA descriptor indices, current transfer counts, interrupt status/ack bits, firmware status, timer counts, scratch registers, byte counters, power FSM status, wakeup state, and I2S FIFO/status fields. Persistence and reset semantics are hardware-defined and handled by the drivers that use these addresses.

## Dependencies and integration points
The immediate integration point is `sources/distributed-fs/ceph-client/sound/soc/amd/acp.h`, which includes this header together with `acp_2_2_sh_mask.h`. The older ACP PCM DMA code relies on both headers to program DMA channels and I2S controller instances. The offset values are dword register indices in the ACP 2.2 register documentation style, so call sites must use the same address-unit convention expected by the local register accessor macros/helpers.

This file is independent of the newer `ps/acp63.h` path. `acp63.h` includes a different offset source, `<sound/acp63_chip_offset_byte.h>`, for ACP6.3/7.x byte offsets.

## Risks and edge cases
The main risk is silent hardware misprogramming if any offset is wrong, if a caller treats a dword offset as a byte offset, or if an ACP generation mismatch causes ACP2.2 offsets to be used on a newer block. Because these macros are untyped, the compiler cannot catch use of the wrong register bank or read/write direction. The repeated per-channel and per-DSP patterns also make copy/paste mistakes hard to see in review.

Another risk is stale generated documentation: this header carries an MIT license and 2014 AMD copyright, while newer ACP drivers use separate ACP6.3/7.x register definitions. Maintainers should avoid extending this file for unrelated ACP generations unless the hardware documentation confirms binary compatibility.

## Test signals
Useful validation is mostly integration or hardware-facing:

- Build coverage for drivers that include `sound/soc/amd/acp.h` catches missing or renamed macros.
- Boot/probe tests on ACP2.2-era hardware should confirm ACP power-on/reset, DMA descriptor programming, and I2S playback/capture still work.
- ALSA PCM playback/capture tests exercise the DMA/I2S offsets indirectly through stream startup, period interrupts, byte counters, underrun/overrun behavior, and shutdown.
- Register readback/debug traces can compare accessed offsets against ACP 2.2 hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_enum.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_enum.h

## Purpose
`acp_2_2_enum.h` is a generated-style hardware enumeration header for AMD ACP/GPU-adjacent register documentation. It defines C `typedef enum` types and numeric symbolic values used to interpret or program register fields. Unlike `acp_2_2_d.h` and `acp_2_2_sh_mask.h`, it is not included by `sound/soc/amd/acp.h` in this tree, and no direct in-scope include use was found in the AMD ASoC subtree. It remains a source of hardware-documentation constants for ACP 2.2 related code or downstream users.

The contents are broader than audio-only ACP. They include debug block identifiers, surface endian and tiling modes, color/depth/image/buffer formats, memory/cache request modes, perfmon modes, surface layout enums, and ACP memory-power force/select controls.

## Important APIs, types, and constants
The file exports only enum types. Important families include:

- `DebugBlockId` plus `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`, which encode debug block IDs at different grouping/stride granularities. These list many GPU blocks such as VMC, SRBM, GRBM, SDMA, SQ, TCP, TCC, TA, TD, LDS, and reserved/unused slots.
- Surface and memory layout enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`.
- Render/data format enums: `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`.
- Tiling detail enums: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, and `MacroTileAspect`.
- Cache/performance/system enums: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- ACP-relevant memory power enums: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

There are no function prototypes, structs, macros, or inline helpers in this file.

## Control flow
There is no runtime control flow. If included, the C compiler makes these enum constants available to code that needs stable symbolic names for register-field values. Because this specific source tree does not show direct include usage for this header in the AMD audio subtree, its practical flow here is archival/generated hardware documentation rather than active execution.

## State and persistence behavior
The header has no software state and no persistence. The enum values describe possible hardware register field values. When used by callers, those values may influence persistent hardware state such as memory tiling configuration, cache policy, perfmon mode, or ACP memory power mode, but no such writes happen in this file.

## Dependencies and integration points
The header is self-contained apart from standard C enum syntax and its include guard. It pairs conceptually with the ACP2.2 offset and mask headers: offsets name registers, masks name bit fields, and enums can name legal field values. Within this repository snapshot, the direct integration is weak because `sound/soc/amd/acp.h` includes only `acp_2_2_d.h` and `acp_2_2_sh_mask.h`.

The broader integration point is generated AMD hardware register documentation. Downstream code that programs debug, tiling, format, perfmon, or ACP memory-power fields can include this header to avoid raw numeric literals.

## Risks and edge cases
Because these are hardware ABI values, changing names or numeric assignments can break register programming even when C compilation succeeds. The debug-block lists contain many `UNUSED` and reserved entries; using those as valid hardware targets could produce undefined hardware behavior. The file also mixes audio-adjacent ACP memory-power enums with graphics/display-oriented surface and format enums, so maintainers should not assume every enum is meaningful to the ALSA ACP drivers.

Another risk is dead/stale documentation: lack of current in-tree users means build tests may not catch accidental breakage until an external user includes it.

## Test signals
Test signals are mostly compile and hardware validation in code that includes this header:

- A full kernel build with any user that includes `acp_2_2_enum.h` catches syntax and renamed-type breakage.
- Static searches should confirm whether enum values are actively consumed before refactoring.
- Hardware tests for any driver using these values should validate register programming against expected modes, especially memory-power mode transitions and perfmon/debug block selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_sh_mask.h

## Purpose
`acp_2_2_sh_mask.h` is the ACP 2.2 register bit-field companion to `acp_2_2_d.h`. It exports preprocessor constants for each documented field's mask and shift, using names like `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. The legacy AMD ACP audio header `sound/soc/amd/acp.h` includes this file after the offset map, giving ACP2.2-era driver code the field definitions needed to construct and decode MMIO register values.

There are no functions or executable statements. The file is an ABI map for DMA control, descriptor status, DSP memory windows and reset controls, DAGB/AXI bridge configuration and errors, global ACP reset/clock/power fields, interrupt masks/status/acks, semaphores, SRBM indexed access, firmware/timer/scratch registers, efuse and power-gating fields, voice wakeup controls, ACP memory sleep/shutdown fields, and I2S controller fields.

## Important APIs, types, and constants
The exported API is the mask/shift macro namespace. Important groups are:

- DMA channel fields for channels 0-15: `DMAChRst`, `DMAChRun`, `DMAChIOCEn`, `Circular_DMA_En`, `DMAChGracefulRstEn`, descriptor start index/count/current index, current transfer count, priority, terminal error, and error code.
- Global DMA fields: descriptor base address, maximum descriptors, channel status bitmap, and channel grouping.
- DSP0/DSP1/DSP2 fields: cache and noncache window offset/size, onion/garlic select, page enable, debug PC, NMI select, clock enable, soft reset, reset done, clock status, run-stall, halt-on-reset, wait mode, vector select, and debug registers.
- AXI2DAGB onion/garlic fields: data swap, multiple read/write request enables, max read burst, stall behavior, NACK/address-window violation checks, urgency, error status sources/overflow/valid bits, transaction performance counters, page group sizes, base addresses, snoop/target memory select, group enable, and ATU cache invalidation.
- ACP global fields: clock enable/status, JTAG enable, reference clock/stutter status, soft-reset control and done bits, SCLK sleep control, SMU mailbox, and future/reserved full-register fields.
- Interrupt/error fields: external interrupt enables/masks/status/acks, ACP error source status, DSP software interrupt trigger/control/status, DSP interrupt control/status for three DSPs, timeout values and counter enables, and external timers.
- Semaphore/SRBM fields: global semaphores 0-47, SRBM client base/read/cycle/index/data fields, and semaphore command/status/request address fields.
- Power and pad fields: efuse disable bits, PGFSM retain/config/write/read fields, ACP IP PGFSM access, I2S pin config, Azalia/I2S select, package/pad pull controls, BT UART pad select, memory shutdown/deep-sleep/wakeup request/status fields.
- I2S fields: speaker, mic/speaker, and Bluetooth I2S enable, RX/TX enable, clock control, channel enable, word length, ISR/IMR overrun/empty bits, FIFO flush/status, DMA address/control fields, and component parameter/version/type fields.

## Control flow
There is no local control flow. In use, the flow is:

1. A driver includes `acp.h`, receiving ACP2.2 offsets and bit-field masks.
2. The driver reads a register, clears or sets fields with these masks/shifts, and writes the result back.
3. Status paths decode fields such as DMA errors, interrupt status, byte counters, or power FSM state using the same constants.

The file does not provide field-preparation helpers; call sites must perform shifting/masking correctly or use kernel bitfield helpers when available.

## State and persistence behavior
No software state is stored. The macros describe mutable hardware state. Several fields are status/ack fields with write-one-to-clear style semantics in hardware; others control persistent runtime configuration such as DMA channel enable, circular DMA, DSP reset/run-stall, interrupt masks, DAGB address windows, and memory sleep/shutdown. Incorrect writes can outlive a single function call until reset or power-cycle.

## Dependencies and integration points
`sound/soc/amd/acp.h` is the direct in-tree include point. It combines this header with `acp_2_2_d.h`, then defines ACP DMA channel numbers, descriptor indices, SRAM banks, platform data, and DMA descriptor structures for older ACP PCM code. The mask names are tied to the `mm...` register offsets by naming convention rather than by typed structures.

The header is independent of the newer Pink Sardine `ps/acp63.h`, which uses byte-offset definitions from `acp63_chip_offset_byte.h`. Mixing ACP2.2 mask definitions with ACP6.3/7.x register offsets would be unsafe unless the register documentation explicitly guarantees compatibility for the specific field.

## Risks and edge cases
The largest risk is untyped bit manipulation. A field mask can be applied to the wrong register without compiler diagnostics. Repeated register banks also increase the chance of selecting a channel/DSP/I2S instance with a plausible but wrong macro name. Status and ack fields share masks for several interrupt registers; code must know whether it is reading status or writing an ack.

Hardware side effects are also significant. DMA run/reset bits, DSP reset/run-stall fields, interrupt enables, and memory power controls can stop audio streams or hang device initialization if programmed in the wrong order. Generated headers like this also tend to have limited direct unit coverage; many mistakes surface only on affected hardware.

## Test signals
Useful signals include:

- Build coverage for ACP2.2 legacy AMD ASoC drivers that include `acp.h`.
- Runtime ALSA playback/capture on ACP2.2 hardware, validating stream start/stop, period interrupts, byte counters, and error-free suspend/resume.
- IRQ storm/underrun/overrun tests around I2S FIFO and DMA IOC masks.
- Register trace or debugfs-style readback comparing programmed register values with expected masks/shifts.
- Static checks for raw literals that should use these macros, and for use of ACP2.2 macros in non-ACP2.2 driver paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/mach-config.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/mach-config.h

## Purpose
`mach-config.h` is the shared AMD ASoC machine-configuration contract used by ACP legacy, SOF, SoundWire, and Pink Sardine PCI drivers. It defines common configuration flags, the AMD ACP PCI device ID, extern declarations for ACPI machine tables, and `struct config_entry`, the DMI/device table shape used by `acp-config.c` to choose between SOF and legacy machine paths.

The header is intentionally small but sits on a key policy boundary: PCI and SOF drivers call `snd_amd_acp_find_config()` from `acp-config.c`, which uses the flags and table type declared here to decide whether a given system should bind a SOF driver, a legacy driver, DMIC-only mode, SoundWire machines, or no driver in that lane.

## Important APIs, types, and constants
Important constants:

- `FLAG_AMD_SOF`, `FLAG_AMD_SOF_ONLY_DMIC`, `FLAG_AMD_LEGACY`, and `FLAG_AMD_LEGACY_ONLY_DMIC` are bit flags used as configuration outcomes and quirks. They are defined with `BIT(n)` and therefore depend on Linux bit helpers being available through included headers.
- `ACP_PCI_DEV_ID` is `0x15E2`, the common AMD ACP PCI device ID used by the configuration lookup and by related PCI drivers.

Extern machine arrays:

- `snd_soc_acpi_amd_sof_machines`
- `snd_soc_acpi_amd_rmb_sof_machines`
- `snd_soc_acpi_amd_vangogh_sof_machines`
- `snd_soc_acpi_amd_acp63_sof_machines`
- `snd_soc_acpi_amd_acp63_sdw_machines`
- `snd_soc_acpi_amd_acp63_sof_sdw_machines`
- `snd_soc_acpi_amd_acp70_sof_machines`
- `snd_soc_acpi_amd_acp70_sdw_machines`
- `snd_soc_acpi_amd_acp70_sof_sdw_machines`

These arrays are consumed by platform/SOF matching code to locate `struct snd_soc_acpi_mach` descriptors.

`struct config_entry` contains `u32 flags`, `u16 device`, and `const struct dmi_system_id *dmi_table`. `acp-config.c` instantiates arrays of this type to match PCI device IDs and DMI systems.

## Control flow
The header itself has no executable control flow. The main flow enabled by it is:

1. ACP/SOF PCI code includes this header and calls `snd_amd_acp_find_config(pci)`.
2. `acp-config.c` checks PCI revision and either reads `acp-audio-config-flag` from ACPI for ACP 7.0+ or scans `config_entry` DMI rows for older platforms.
3. The returned flag controls whether a driver continues probing or defers to another lane. For example, `ps/pci-ps.c` returns `-ENODEV` when a nonzero config flag is defined, allowing the selected SOF/legacy path to own the hardware.
4. Machine table externs are used by SOF and ACP machine-selection code to bind the right topology/driver for ACPI IDs and SoundWire links.

## State and persistence behavior
The header stores no state. It declares static configuration categories and external machine table symbols. The stateful part lives in `acp-config.c`, where `acp_quirk_data` stores the selected flag for machine table private data. The outcome depends on platform firmware data: PCI revision, ACPI properties, and DMI strings.

## Dependencies and integration points
The header includes `<sound/soc-acpi.h>` for `struct snd_soc_acpi_mach`. It also uses `struct dmi_system_id` in `struct config_entry`; the concrete users include Linux DMI headers before instantiating tables. Integration points found in this tree include:

- `sound/soc/amd/acp-config.c`, which defines `snd_amd_acp_find_config()` and several machine arrays.
- AMD ACP legacy/common PCI code under `sound/soc/amd/acp/`.
- Pink Sardine PCI code `sound/soc/amd/ps/pci-ps.c`.
- SOF AMD PCI drivers under `sound/soc/sof/amd/`.
- ACP63/ACP70 ACPI match files that define machine tables declared here.

## Risks and edge cases
Configuration flags decide driver ownership. A wrong flag can bind the wrong audio stack, suppress the intended PCI driver, or expose only DMIC when SoundWire/SOF support should be active. DMI matching is brittle because vendor/product/version strings must exactly match firmware. For ACP 7.0+ systems, ACPI `acp-audio-config-flag` is authoritative except for the explicit ASUS override in `acp-config.c`; missing or bad firmware properties can alter probe behavior.

The shared `ACP_PCI_DEV_ID` constant also means unrelated ACP generations pass through the same top-level matching path, so revision checks in consumers remain important.

## Test signals
Good validation includes:

- Build tests for AMD ASoC and SOF configurations that include this header.
- Boot/probe logs on systems in the DMI table and on ACP7.x systems with ACPI `acp-audio-config-flag`.
- Confirmation that exactly the intended PCI/SOF/legacy driver binds and that alternative drivers return `-ENODEV`.
- ALSA card enumeration and topology loading for the selected machine table.
- DMI/ACPI regression tests when adding a platform quirk or new machine array declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/mach-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/ps/Makefile

## Purpose
This Makefile wires the AMD Pink Sardine (`ps`) ASoC platform objects into the kernel build. It declares composite module object lists for the ACP PCI/common layer, the PDM DMA engine, the SoundWire DMA engine, and the DMIC machine driver, then attaches those modules to Kconfig symbols.

The file has no runtime code, but it defines which C files are linked together and which features appear when `CONFIG_SND_SOC_AMD_PS` or `CONFIG_SND_SOC_AMD_PS_MACH` is enabled.

## Important APIs, types, and build targets
Composite targets:

- `snd-pci-ps-y := pci-ps.o ps-common.o` links the common PCI driver with platform-specific hardware operation callbacks from `ps-common.c`.
- `snd-ps-pdm-dma-y := ps-pdm-dma.o` builds the ACP PDM DMA component.
- `snd-soc-ps-mach-y := ps-mach.o` builds the Pink Sardine DMIC machine driver.
- `snd-ps-sdw-dma-y := ps-sdw-dma.o` builds the ACP SoundWire DMA component.

Kconfig-driven objects:

- `obj-$(CONFIG_SND_SOC_AMD_PS)` includes `snd-pci-ps.o`, `snd-ps-pdm-dma.o`, and `snd-ps-sdw-dma.o`.
- `obj-$(CONFIG_SND_SOC_AMD_PS_MACH)` includes `snd-soc-ps-mach.o`.

## Control flow
Build-time flow:

1. Kbuild evaluates the relevant Kconfig symbols.
2. If `CONFIG_SND_SOC_AMD_PS` is enabled, the PCI driver and both DMA platform components are built.
3. If `CONFIG_SND_SOC_AMD_PS_MACH` is enabled, the DMIC-only machine driver is built.
4. At runtime, `pci-ps.c` probes ACP6.3/7.x PCI devices, calls hardware ops from `ps-common.c`, and registers platform devices named for the PDM and SoundWire DMA modules. `ps-mach.c` can then bind the DMIC card when the PCI layer registers the `acp_ps_mach` platform device.

## State and persistence behavior
The Makefile stores no runtime state. Its build selections influence persistent kernel/module artifacts: which `.o` files are linked into built-in code or loadable modules, which platform drivers are registered, and whether runtime platform-device registration can find a matching driver.

## Dependencies and integration points
The Makefile depends on Kconfig symbols defined elsewhere in the AMD ASoC tree, especially `CONFIG_SND_SOC_AMD_PS` and `CONFIG_SND_SOC_AMD_PS_MACH`. Its targets correspond to source files in the same directory:

- `pci-ps.c` and `ps-common.c` depend on `acp63.h` for shared constants, data structures, and hardware-op declarations.
- `ps-pdm-dma.c` and `ps-sdw-dma.c` expose ALSA component/platform functionality used by machine drivers and SoundWire managers.
- `ps-mach.c` registers the DMIC capture card that references the `acp_ps_pdm_dma.0` CPU/platform DAI and `dmic-codec.0`.

## Risks and edge cases
If `CONFIG_SND_SOC_AMD_PS` is enabled without the machine driver for a DMIC-only configuration, the PCI and PDM DMA pieces may probe but no complete ALSA card will appear for that path. Conversely, building `CONFIG_SND_SOC_AMD_PS_MACH` without the platform device producer would leave the machine driver with nothing to bind. Splitting `pci-ps.o` from `ps-common.o` would break hardware operation resolution because the PCI probe initializes callbacks declared in `acp63.h` and defined in `ps-common.c`.

SoundWire support also depends on broader SoundWire and ACPI support; this Makefile builds the DMA side under `CONFIG_SND_SOC_AMD_PS`, but runtime SoundWire probing still depends on the rest of the kernel configuration and firmware description.

## Test signals
Useful checks include:

- Kernel build with `CONFIG_SND_SOC_AMD_PS=m/y` and `CONFIG_SND_SOC_AMD_PS_MACH=m/y`.
- Module inspection confirming expected modules or built-in objects include `snd-pci-ps`, `snd-ps-pdm-dma`, `snd-ps-sdw-dma`, and `snd-soc-ps-mach`.
- Boot probe on ACP6.3/7.x systems verifying the PCI module registers PDM/SoundWire platform devices and matching component drivers bind.
- ALSA card enumeration for DMIC-only and SoundWire configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/acp63.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/ps/acp63.h

## Purpose
`ps/acp63.h` is the shared private interface for the AMD Pink Sardine ACP PCI, PDM DMA, SoundWire DMA, machine, and hardware-callback code. Despite the filename, it covers ACP6.3, ACP7.0, ACP7.1, and ACP7.2 style platforms. It centralizes device IDs, register range constants, power/reset/status masks, DMA buffer geometry, PDM and SoundWire memory-window layout, interrupt bit mappings, stream enums, runtime data structures, hardware operation callbacks, inline dispatcher helpers, and the exported configuration lookup prototype.

This file is active in the PS driver path: `pci-ps.c`, `ps-common.c`, `ps-pdm-dma.c`, `ps-sdw-dma.c`, and `ps-mach.c` include it.

## Important APIs, types, and constants
Platform identity and register geometry:

- `ACP_DEVICE_ID` is `0x15E2`.
- `ACP63_REG_START`/`ACP63_REG_END` define the MMIO register window range used when registering child platform resources.
- `ACP63_PCI_REV`, `ACP70_PCI_REV`, `ACP71_PCI_REV`, and `ACP72_PCI_REV` select generation-specific hardware ops and DMA interrupt mappings.

Power, reset, timing, and status constants:

- `ACP_SOFT_RESET_SOFTRESET_AUDDONE_MASK`, `ACP63_PGFSM_*`, `ACP70_PGFSM_*`, `ACP63_TIMEOUT`, `ACP70_TIMEOUT`, `DELAY_US`, `ACP_DELAY_US`, and `ACP_COUNTER` are used by `ps-common.c` polling flows.
- `ACP_ERROR_IRQ`, `ACP_ERROR_MASK`, `ACP_EXT_INTR_STAT_CLEAR_MASK`, `PDM_DMA_STAT`, and `PDM_DMA_INTR_MASK` describe interrupt and error handling.
- `ACP_SUSPEND_DELAY_MS` defines runtime suspend delay policy for the PCI driver.

PDM constants:

- Capture hardware limits are fixed by `CAPTURE_*`, `MAX_BUFFER`, and `MIN_BUFFER`.
- `ACP_DMIC_DEV`, `ACP63_DMIC_ADDR`, `PDM_DECIMATION_FACTOR`, `ACP_PDM_CLK_FREQ_MASK`, `ACP_WOV_GAIN_CONTROL`, `ACP_PDM_ENABLE`, `ACP_PDM_DISABLE`, and `ACP_PDM_DMA_EN_STATUS` are used by `ps-pdm-dma.c`.
- `ACP_SRAM_PTE_OFFSET`, `PDM_PTE_OFFSET`, `PDM_MEM_WINDOW_START`, and `PAGE_SIZE_4K_ENABLE` configure DMA page tables and memory windows.

SoundWire constants:

- `ACP63_SDW_ADDR`, `AMD_SDW_MAX_MANAGERS`, `ACP_SDW0_STAT`, `ACP_SDW1_STAT`, and SDW DMA IRQ masks define discovery and IRQ handling.
- `ACP63_SDW0_DMA_MAX_STREAMS`, `ACP63_SDW1_DMA_MAX_STREAMS`, `ACP70_SDW0_DMA_MAX_STREAMS`, and `ACP70_SDW1_DMA_MAX_STREAMS` size stream arrays.
- `ACP63_SDW0_DMA_TX_IRQ_MASK(i)`, `ACP63_SDW0_DMA_RX_IRQ_MASK(i)`, `ACP63_SDW1_DMA_IRQ_MASK(i)`, `ACP70_SDW0_DMA_TX_IRQ_MASK(i)`, `ACP70_SDW0_DMA_RX_IRQ_MASK(i)`, `ACP70_SDW1_DMA_TX_IRQ_MASK(i)`, and `ACP70_SDW1_DMA_RX_IRQ_MASK(i)` encode stream-id to interrupt-bit mappings.
- `SDW_PTE_OFFSET(i)`, `ACP_SDW_FIFO_OFFSET(i)`, and `SDW_MEM_WINDOW_START(i)` compute per-manager SoundWire DMA page table, FIFO, and memory window addresses.

Enums:

- `enum acp_config` enumerates BIOS pin/config values used by hardware callbacks to set `is_pdm_config` and `is_sdw_config`.
- `enum amd_acp63_sdw0_channel`, `enum amd_acp63_sdw1_channel`, and `enum amd_acp70_sdw_channel` define stream IDs for SDW DMA interrupt and runtime stream arrays.

Key structs:

- `struct pdm_stream_instance` stores per-open PDM DMA state: page count, channels, DMA address, byte count, and MMIO base.
- `struct pdm_dev_data` stores PDM component device state: IRQ flag, MMIO base, shared ACP lock pointer, and active capture substream.
- `struct sdw_dma_dev_data` stores SoundWire DMA component state: MMIO base, shared lock, ACP revision, and per-generation/per-manager substream arrays.
- `struct acp_sdw_dma_stream` stores per-open SoundWire stream state: page count, channels, stream ID, manager instance, DMA address, and byte count.
- `union acp_sdw_dma_count` provides high/low and `u64` views for byte counters.
- `struct sdw_dma_ring_buf_reg` groups register offsets needed to program one SoundWire ring buffer.
- `struct acp_hw_ops` is the platform-generation operation table for init/deinit/config/IRQ/suspend/resume callbacks.
- `struct acp63_dev_data` is the PCI driver context, tying together MMIO, resources, child platform devices, locks, SoundWire ACPI/probe context, machine tables, configuration booleans, wake flags, subsystem IDs, saved pad state, and DMA interrupt status arrays.

Inline APIs:

- `acp_hw_init()`, `acp_hw_deinit()`, `acp_hw_get_config()`, `acp_hw_sdw_dma_irq_thread()`, `acp_hw_suspend()`, `acp_hw_resume()`, `acp_hw_suspend_runtime()`, and `acp_hw_runtime_resume()` validate callback presence and dispatch through `struct acp_hw_ops`, returning `-EOPNOTSUPP` for missing integer callbacks.
- `acp63_hw_init_ops()` and `acp70_hw_init_ops()` are declared for `ps-common.c` to populate callback tables.
- `snd_amd_acp_find_config()` is declared for the shared machine-configuration lookup implemented in `acp-config.c`.

## Control flow
The header enables the following runtime flow:

1. `pci-ps.c` probes PCI device `0x15E2`, rejects unsupported revisions, maps MMIO, allocates `struct acp63_dev_data`, selects ACP63 or ACP70 ops using the revision, and calls the inline `acp_hw_init()` wrapper.
2. Generation-specific callbacks from `ps-common.c` power on, reset, enable interrupts, read `ACP_PIN_CONFIG`, and set `is_pdm_config`/`is_sdw_config`.
3. `pci-ps.c` uses ACPI child addresses and `_WOV`/SoundWire discovery to decide whether PDM and/or SoundWire child platform devices exist, then registers `acp_ps_pdm_dma`, `dmic-codec`, `amd_ps_sdw_dma`, and an appropriate machine device.
4. PDM and SoundWire DMA drivers allocate per-stream private structures defined here during PCM open, program page tables/ring buffers in hw_params, enable interrupts, update byte counters for pointer callbacks, and call `snd_pcm_period_elapsed()` when the PCI IRQ path marks a stream interrupt.
5. PCI IRQ handling in `pci-ps.c` decodes ACP external interrupt registers, updates the interrupt-status arrays in `struct acp63_dev_data`, and invokes `acp_hw_sdw_dma_irq_thread()` for generation-specific period-elapsed handling.
6. Suspend/resume wrappers call generation-specific ops that either deinitialize ACP or preserve SoundWire wake/pad state depending on current device state.

## State and persistence behavior
`struct acp63_dev_data` is the long-lived PCI driver state and owns most cross-component state. Its lock protects shared ACP register access passed down to PDM and SoundWire DMA child data. The child platform devices store pointers back to their component data with active ALSA substreams, while per-open stream structs are allocated and attached to `runtime->private_data`.

Hardware state persists in ACP MMIO registers: power FSM state, reset status, interrupt masks/status, PDM and SoundWire DMA page tables in ACP scratch/SRAM windows, ring-buffer addresses/sizes, FIFO configuration, byte counters, wake enable/status, and pad keeper/pulldown settings. Suspend/resume code explicitly saves some pad state and preserves SoundWire wake state when needed.

## Dependencies and integration points
The header includes `<linux/soundwire/sdw_amd.h>` for AMD SoundWire manager types and `<sound/acp63_chip_offset_byte.h>` for byte-offset register constants. It depends on common Linux kernel types and APIs used by includers: `struct pci_dev`, `struct device`, `struct platform_device`, `struct resource`, `struct mutex`, `struct snd_pcm_substream`, `dma_addr_t`, `void __iomem`, `BIT()`, and errno constants.

Major integration points:

- `ps/pci-ps.c` owns PCI probe/remove/IRQ/PM orchestration and child platform registration.
- `ps/ps-common.c` defines ACP63 and ACP70 hardware callbacks and fills `struct acp_hw_ops`.
- `ps/ps-pdm-dma.c` uses PDM buffer limits, PTE offsets, interrupt masks, and PDM stream/device data structures.
- `ps/ps-sdw-dma.c` uses SoundWire stream enums, IRQ masks, ring-buffer layout, stream/device structs, and generation-specific max-stream constants.
- `ps/ps-mach.c` uses the PDM platform naming contract to register a DMIC-only ASoC card.
- `mach-config.h`/`acp-config.c` provide `snd_amd_acp_find_config()`, which affects whether the PS PCI driver binds.

## Risks and edge cases
Revision-specific branching is central. Using ACP63 stream counts or interrupt mappings on ACP70/ACP71/ACP72 can route period interrupts to the wrong substream or miss them entirely. The `ACP_HW_OPS(acp_data, cb)` macro assumes `hw_ops` and callback members are valid; the inline wrappers guard that, so direct macro use should remain limited.

The shared `acp63_base` name is historical and covers ACP70+ too, which can obscure generation-specific offset differences. PDM and SoundWire DMA page-table offsets, memory windows, and ring-buffer spacing are hard-coded hardware contracts; overlapping windows would corrupt DMA. IRQ masks are write/clear sensitive and protected only where code takes `acp_lock`; missing locking around shared interrupt-control registers can lose bits when PDM and SoundWire paths update masks concurrently.

The inline suspend/runtime-resume wrappers return `-EOPNOTSUPP` if callbacks are absent. PM code should treat that as a real unsupported operation, not as success. Documentation comments also contain minor typos and stale names, so field names in code should be trusted over prose.

## Test signals
High-value validation includes:

- Build coverage for `CONFIG_SND_SOC_AMD_PS`, `CONFIG_SND_SOC_AMD_PS_MACH`, and SoundWire-enabled/disabled configurations.
- PCI probe on ACP6.3, ACP7.0, ACP7.1, and ACP7.2 revisions, confirming the correct hardware ops are selected.
- PDM capture tests at 48 kHz/S32_LE with fixed period and buffer limits, checking DMA start/stop, pointer movement, and period interrupts.
- SoundWire playback/capture tests across both managers and all supported stream IDs, checking stream-to-IRQ mapping and period elapsed callbacks.
- Suspend/resume and runtime PM tests with active and idle PDM/SoundWire streams, including ACP70 host-wake/PME paths and pad-state restoration.
- Fault-injection or register-debug tests for ACP error IRQ handling and DMA timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/acp63.h -->
