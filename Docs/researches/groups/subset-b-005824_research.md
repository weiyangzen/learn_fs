# subset-b-005824 Research

Grouped research for Linux device-tree binding headers under `sources/distributed-fs/ceph-client/include/dt-bindings`. These files export preprocessor constants used by DTS/DTSI sources and kernel drivers; their observable behavior is the numeric ABI they define rather than runtime control flow.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra186-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra186-clock.h

## Purpose
Defines Tegra186 BPMP clock identifiers for device-tree `clocks` references and clock provider lookups. The file is a large numeric ABI map, with Doxygen groups documenting functional domains such as external inputs, display, camera, audio, UART, I2C, SPI, storage, PWM, PLLs, CPU, host, memory, power-domain, and peripheral clocks.

## Important APIs, Types, and Constants
Exports `TEGRA186_CLK_*` integer macros, beginning with low IDs such as `TEGRA186_CLK_FUSE` and `TEGRA186_CLK_GPU`, extending through higher BPMP-managed clock IDs, and ending with `TEGRA186_CLK_CLK_MAX` at 624. There are no C types or functions. The key API is the stable macro namespace consumed by DTS files and Tegra clock/BPMP drivers.

## Control Flow and State
There is no executable control flow. Include-guard handling is the only preprocessor flow. Runtime state lives in the Tegra BPMP firmware and kernel clock framework; this header only supplies compile-time identifiers that select clock resources.

## Dependencies and Integration Points
The header has no includes. Integration is through device-tree source compilation, clock specifier cells, Tegra BPMP firmware protocol tables, and drivers that call common clock framework APIs after resolving IDs from DT.

## Risks and Test Signals
The major risk is ABI drift: renumbering, deleting, or reusing a macro can point a DT clock reference at the wrong hardware clock. Sparse numbering and documented groups should be preserved. Test signals include successful `dtbs_check`, clean kernel build coverage for Tegra186 DTs, and boot/runtime validation that devices can acquire and enable their referenced clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra186-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra194-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra194-clock.h

## Purpose
Defines Tegra194 clock IDs for DT bindings and BPMP clock access. It covers SoC clocks for display, audio, storage, I/O, fabric, CPU, PLL, PCIe, UFS, XUSB, MIPI, and always-on domains.

## Important APIs, Types, and Constants
The exported API is the `TEGRA194_CLK_*` macro set. IDs start at `TEGRA194_CLK_ACTMON` 1 and run through entries such as `TEGRA194_CLK_NAFLL_*`, `TEGRA194_CLK_PEX*`, `TEGRA194_CLK_UFS*`, and `TEGRA194_CLK_PLLE_HPS` 326. There are 313 numeric clock definitions and no functions or structs.

## Control Flow and State
This header has no runtime path. The only flow is the include guard `__ABI_MACH_T194_CLOCK_H`. State is external: the selected numeric ID is interpreted by the Tegra BPMP clock provider and common clock framework.

## Dependencies and Integration Points
No local includes are required. DTS clock specifiers include this header and pass IDs to Tegra194 clock provider nodes. Kernel drivers indirectly depend on these constants through DT resources such as `clocks` and `assigned-clocks`.

## Risks and Test Signals
Numeric values are DT ABI and must remain stable. Holes in the sequence are intentional compatibility space, not cleanup opportunities. Good signals are `dtbs_check`, Tegra194 DTS compilation, and boot tests that exercise display, storage, network, PCIe, and audio clock requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra194-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra20-car.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra20-car.h

## Purpose
Provides Tegra20 Clock and Reset controller clock IDs for device-tree users. It maps older Tegra CAR module and PLL clocks to stable integers.

## Important APIs, Types, and Constants
The file exports `TEGRA20_CLK_*` macros, including CPU, AC97, RTC, timers, UARTs, GPIO, SDMMC, I2C, SPI, display, memory, PLL, audio, and TWD clocks. `TEGRA20_CLK_CLK_MAX` is 133. Some comments document aliases such as `TEGRA20_CLK_COP` as AVP and `TEGRA20_CLK_AUDIO` as `audio_sync_clk`.

## Control Flow and State
No runtime logic exists. The include guard `_DT_BINDINGS_CLOCK_TEGRA20_CAR_H` prevents duplicate expansion. Clock enable/rate state is owned by Tegra20 CAR hardware and the kernel clock driver.

## Dependencies and Integration Points
There are no includes. Integration is through DT source files and the Tegra20 CAR clock provider, which must use the same numbering when resolving clock specifiers.

## Risks and Test Signals
Because this header supports legacy DTs, even comments that explain aliases can be important for maintainers. Renumbering can break old boards silently. Test signals include old Tegra20 DTS builds, schema validation, and runtime probing of devices that depend on module clocks such as SDMMC, UART, display, and audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra20-car.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra210-car.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra210-car.h

## Purpose
Defines Tegra210 CAR clock identifiers for DT clock consumers. It extends the classic Tegra CAR binding model with IDs for Tegra210 peripheral, PLL, audio, display, camera, memory, and synchronization clocks.

## Important APIs, Types, and Constants
The exported `TEGRA210_CLK_*` constants include module IDs beginning around the legacy CAR range, PLL outputs, display/DSI/SOR clocks, XUSB clocks, audio hub and I2S clocks, EMC, MIPI calibration, and DMIC sync clocks. `TEGRA210_CLK_CLK_MAX` is 394. No C types or callable helpers are defined.

## Control Flow and State
The header has include-guard-only preprocessor control flow. Runtime control is performed by Tegra210 clock/reset hardware and kernel providers; this file only names indexes.

## Dependencies and Integration Points
No includes. Device-tree files include it for `clocks`, `resets`, and assigned clock properties, while the Tegra210 clock driver consumes the same ID space.

## Risks and Test Signals
Clock IDs are ABI. Gaps and historical numbering should not be compacted. Tests should include DT compilation, `dtbs_check`, and board boot coverage for high-risk domains such as display, audio, USB, storage, camera, and EMC rate control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra210-car.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra234-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra234-clock.h

## Purpose
Defines Tegra234 clock IDs used by DT and BPMP-managed clock providers. Inline comments link many constants to hardware mux, gate, divider, and PLL registers, making this both an ABI map and a hardware-reference index.

## Important APIs, Types, and Constants
Exports `TEGRA234_CLK_*` constants from `TEGRA234_CLK_ACTMON` 1 through memory-controller related IDs up to `TEGRA234_CLK_EMCSD_MC` 476. Important groups include audio, CAN, I2C, I2S sync inputs, EQOS, display, NVENC/NVDEC/NVJPG, XUSB, UFS, PCIe, PLLs, AON, host, and EMC. `TEGRA234_CLK_EMC` is documented as a special rate-control path that triggers memory-controller clock switching sequences.

## Control Flow and State
No executable logic is present. The comments describe expected behavior of consumers, especially for clocks whose rate setting has side effects in firmware. Runtime state is held by BPMP firmware, clock hardware, and the common clock framework.

## Dependencies and Integration Points
The header is self-contained and guarded by `DT_BINDINGS_CLOCK_TEGRA234_CLOCK_H`. It integrates with Tegra234 DTs, assigned clock properties, BPMP firmware protocol tables, and drivers that request clocks by phandle/index.

## Risks and Test Signals
The risk is high because IDs cross a firmware boundary. Renumbering, altering special comments without matching provider behavior, or adding IDs that conflict with firmware tables can break boot, display, networking, or memory scaling. Test signals include DT schema validation, Tegra234 DT build coverage, BPMP clock query tests, and runtime exercises of EMC, display, PCIe, UFS, EQOS, and audio clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra234-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra30-car.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra30-car.h

## Purpose
Provides Tegra30 CAR clock IDs for device-tree references. It names legacy module clocks, PLL outputs, audio muxes, display, camera, and pad clocks.

## Important APIs, Types, and Constants
The `TEGRA30_CLK_*` namespace starts with `TEGRA30_CLK_CPU` 0, includes peripheral clocks such as UART, I2C, SPI, SDMMC, display, HDMI, USB, and memory, and ends with camera pad IDs `TEGRA30_CLK_CSIA_PAD` and `TEGRA30_CLK_CSIB_PAD` at 309 and 310. No function-like macros are exported.

## Control Flow and State
There is no executable flow. The include guard prevents duplicate definitions. Hardware state is controlled by the Tegra30 CAR driver and reset/clock registers.

## Dependencies and Integration Points
Self-contained header included by Tegra30 DTS/DTSI files and matched by the Tegra30 clock provider implementation.

## Risks and Test Signals
The IDs preserve legacy board ABI and include non-contiguous values. Do not reorder or close gaps. Test signals are DT compilation, schema validation, and runtime probing for display, audio, storage, USB, and camera users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra30-car.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tenstorrent,atlantis-prcm-rcpu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tenstorrent,atlantis-prcm-rcpu.h

## Purpose
Defines clock and reset IDs for the Tenstorrent Atlantis PRCM RCPU block. It supplies DT-facing identifiers for root/divided RCPU clocks, peripheral clocks, interconnect clocks, and reset lines.

## Important APIs, Types, and Constants
The file exports `CLK_*` IDs, including `CLK_RCPU_PLL`, `CLK_RCPU_ROOT`, divided RCPU clocks, RTC, DMA, AXI/APB fabric, UART, SPI, GPIO, CAN, and I2S clocks. It also exports `RST_*` reset IDs ending with `RST_I2S1` 31. There are no structs or helper macros.

## Control Flow and State
No executable control flow. Runtime state belongs to the PRCM clock/reset provider and reset controller; DT consumers only pass these integer IDs.

## Dependencies and Integration Points
Self-contained and guarded by `_DT_BINDINGS_ATLANTIS_PRCM_RCPU_H`. It integrates with clock-controller and reset-controller nodes for Atlantis RCPU peripherals and bus fabric.

## Risks and Test Signals
Clock and reset namespaces are both present, so consumers must use the right property and provider. Renumbering can bind devices to wrong resets or clocks. Test signals include DTS build, schema checks for PRCM nodes, and boot/probe coverage for UART, SPI, GPIO, CAN, I2S, and DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/tenstorrent,atlantis-prcm-rcpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/thead,th1520-clk-ap.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/thead,th1520-clk-ap.h

## Purpose
Defines application-processor clock IDs for the T-Head TH1520 SoC. It provides DT constants for PLLs, CPU and bus clocks, media/display clocks, peripheral clocks, security clocks, and I/O protection clocks.

## Important APIs, Types, and Constants
Exports `CLK_*` constants such as `CLK_CPU_PLL0`, `CLK_GMAC_PLL`, `CLK_VIDEO_PLL`, `CLK_DPU*`, CPU AXI clocks, GMAC, SDIO/EMMC, UART/I2C/SPI, GPIO, PWM, DPU, HDMI, MIPI DSI pixel clocks, and IOPMP clocks. The numeric ranges are split across functional blocks; there are no helper functions or structs.

## Control Flow and State
The header has no logic beyond `_DT_BINDINGS_CLK_TH1520_H_`. Clock configuration state is owned by TH1520 clock controller hardware and its driver.

## Dependencies and Integration Points
Self-contained DT binding header. It is used by TH1520 DTS files and clock provider code to share a stable ID space.

## Risks and Test Signals
The generic `CLK_*` namespace can collide if included carelessly with other binding headers, so usage is usually limited to DT contexts. ABI risks are wrong IDs for display, storage, or CPU clocks. Test signals are DT compilation, schema validation, and probe coverage for media, GMAC, MMC, UART, and display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/thead,th1520-clk-ap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ti-dra7-atl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ti-dra7-atl.h

## Purpose
Defines DRA7 ATL word-select input IDs used by the TI ATL clock/audio binding. These values identify McASP frame-sync, AHCLK, external reference, and oscillator sources.

## Important APIs, Types, and Constants
Exports `DRA7_ATL_WS_*` macros from `DRA7_ATL_WS_MCASP1_FSR` 0 to `DRA7_ATL_WS_OSC1_X1` 15. The constants enumerate selectable word-select sources rather than clocks in a broad SoC clock tree.

## Control Flow and State
No runtime logic. ATL clock muxing and audio synchronization state are controlled by the TI ATL driver and hardware.

## Dependencies and Integration Points
Self-contained DT binding included by DRA7 audio clock nodes and consumers that select ATL word-select sources.

## Risks and Test Signals
Wrong values can select the wrong audio sync source and cause clocking or sample-rate failures. Test signals include DT schema validation and audio playback/capture tests across McASP and external reference configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ti-dra7-atl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/toshiba,tmpv770x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/toshiba,tmpv770x.h

## Purpose
Defines Toshiba TMPV770X PLL, clock, and reset identifiers for DT bindings. It covers many SoC blocks including CPU, memory, video/image processing, networking, PCIe, USB, NAND, UART, I2C, SPI, PWM, and timer domains.

## Important APIs, Types, and Constants
Exports `TMPV770X_PLL_*`, `TMPV770X_CLK_*`, and `TMPV770X_RESET_*` macros. PLL IDs begin at 0, clock IDs extend to values around 129, and reset IDs are a separate namespace ending with video/image reset constants such as `TMPV770X_RESET_VIIFBS1_L1ISP` 39. There are no helper macros or C declarations.

## Control Flow and State
No executable flow. Clock/reset state is handled by the TMPV770X clock and reset controller drivers.

## Dependencies and Integration Points
The header is self-contained. It integrates with DT clock and reset specifiers for TMPV770X platform devices and the matching provider implementation.

## Risks and Test Signals
Because PLL, clock, and reset identifiers share one header but separate semantic namespaces, wrong use in `clocks` versus `resets` is a key integration risk. Test with DTS builds, schema checks, and probe coverage for image/video, networking, storage, and serial peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/toshiba,tmpv770x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/versaclock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/versaclock.h

## Purpose
Defines output mode constants for the VersaClock clock generator binding. These are DT values describing electrical output type.

## Important APIs, Types, and Constants
Exports `VC5_LVPECL`, `VC5_CMOS`, `VC5_HCSL33`, `VC5_LVDS`, `VC5_CMOS2`, `VC5_CMOSD`, and `VC5_HCSL25`, numbered 0 through 6. There is no include guard in the visible content and no functions or structs.

## Control Flow and State
No control flow or state. Runtime behavior occurs in the VersaClock driver when it interprets output configuration properties.

## Dependencies and Integration Points
Used by DTS nodes for VersaClock-compatible clock generators to select output signaling mode. The matching driver must map these values to register programming.

## Risks and Test Signals
The main risk is mismatched output electrical mode, which can break board-level clock delivery. Test signals include DT schema validation and hardware tests that verify each configured output has the expected signal type and frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/versaclock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/vf610-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/vf610-clock.h

## Purpose
Defines clock IDs for the NXP/Freescale Vybrid VF610 clock controller. It supplies DT-facing identifiers for oscillator, PLL, bus, peripheral, display, audio, DMA, security, and Ethernet switch clocks.

## Important APIs, Types, and Constants
Exports `VF610_CLK_*` constants from `VF610_CLK_DUMMY` 0 through `VF610_CLK_ESW_MAC_TAB3` 195. Groups include SIRC/FIRC oscillators, PLLs and dividers, platform buses, UART, DSPI, I2C, FTM, ENET, SDHC, ADC, DAC, FlexCAN, SAI, display, NFC, DMA, CAAM, CRC, and ESW clocks. No function-like helpers are present.

## Control Flow and State
No runtime flow. Clock state is held by VF610 clock controller registers and the kernel provider.

## Dependencies and Integration Points
The header is self-contained and used by VF610 DTS files and the VF610 clock provider. Consumers reference IDs through clock phandles.

## Risks and Test Signals
Numeric stability is the primary concern. Because `VF610_CLK_DUMMY` is a valid placeholder at zero, consumers and drivers should not treat zero as absent without checking binding semantics. Test signals include DT compilation, schema validation, and boot tests for serial, storage, networking, display, and audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/vf610-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/xlnx-vcu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/xlnx-vcu.h

## Purpose
Defines clock indexes for the Xilinx VCU binding. The IDs describe encoder and decoder core/MCU clocks exposed by the VCU clock provider.

## Important APIs, Types, and Constants
Exports `CLK_XVCU_ENC_CORE`, `CLK_XVCU_ENC_MCU`, `CLK_XVCU_DEC_CORE`, `CLK_XVCU_DEC_MCU`, and `CLK_XVCU_NUM_CLOCKS`. The final macro gives the provider/consumer count of clocks.

## Control Flow and State
No runtime flow or local state. The VCU driver interprets these indexes when acquiring clocks.

## Dependencies and Integration Points
Self-contained DT binding included by Xilinx ZynqMP/VCU DTS nodes and VCU driver code.

## Risks and Test Signals
The count macro should track the highest valid index plus one. Test signals include DT schema validation and media encode/decode probe tests that acquire all four clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/xlnx-vcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/display/sdtv-standards.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/display/sdtv-standards.h

## Purpose
Defines bitmask values for analog SDTV standards in device-tree display bindings. It covers PAL, NTSC, SECAM variants and aggregate masks for standard families and timing groups.

## Important APIs, Types, and Constants
Base bits include `SDTV_STD_PAL_*`, `SDTV_STD_NTSC_*`, and `SDTV_STD_SECAM_*` values. Aggregate masks include `SDTV_STD_PAL`, `SDTV_STD_NTSC`, `SDTV_STD_SECAM`, `SDTV_STD_525_60`, and `SDTV_STD_625_50`. These are bit flags, not ordinal IDs.

## Control Flow and State
No executable logic. The multi-line macros are compile-time OR expressions that define grouped capability masks. Runtime display mode state is owned by encoder/display drivers.

## Dependencies and Integration Points
Self-contained DT binding used by SDTV encoder nodes or display pipeline descriptions that advertise or select supported standards.

## Risks and Test Signals
Risk comes from treating masks as enum values, changing bit assignments, or omitting a variant from aggregate masks. Test signals include preprocessor compilation, DT schema checks, and display validation for PAL/NTSC/SECAM mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/display/sdtv-standards.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/display/tda998x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/display/tda998x.h

## Purpose
Defines audio input mode constants for the NXP TDA998x HDMI transmitter binding.

## Important APIs, Types, and Constants
Exports `TDA998x_SPDIF` value 1 and `TDA998x_I2S` value 2. The mixed-case macro prefix matches the existing binding name and should be preserved for compatibility.

## Control Flow and State
No control flow or state. The HDMI transmitter driver interprets the constants from DT properties.

## Dependencies and Integration Points
Self-contained header included by DTS files configuring TDA998x audio routing.

## Risks and Test Signals
Wrong values select the wrong audio transport and can produce silent HDMI audio. Test signals include DTS compilation, schema validation, and HDMI audio playback tests for SPDIF and I2S configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/display/tda998x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/at91.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/at91.h

## Purpose
Defines Atmel/Microchip AT91 DMA and XDMAC DT configuration encodings. Unlike most files in this set, it includes function-like macros that pack and unpack bitfields for DMA specifier cells.

## Important APIs, Types, and Constants
`AT91_DMA_CFG_PER_ID(id)` masks an 8-bit peripheral ID. XDMAC helpers include `AT91_XDMAC_DT_MEM_IF`, `AT91_XDMAC_DT_GET_MEM_IF`, `AT91_XDMAC_DT_PER_IF`, `AT91_XDMAC_DT_GET_PER_IF`, `AT91_XDMAC_DT_PERID`, and `AT91_XDMAC_DT_GET_PERID`. Offsets place memory interface at bits 13-14, peripheral interface at bits 15-16, and peripheral ID at bits 24-30.

## Control Flow and State
No runtime control flow. The macros are compile-time arithmetic encoders/decoders for DT numeric cells. DMA channel state is external to the header.

## Dependencies and Integration Points
Self-contained binding used by AT91 DMA client nodes and DMA controller drivers parsing `dmas` specifiers.

## Risks and Test Signals
Bitfield overlap or missing parentheses would corrupt DMA request configuration. Tests should compile representative DTS entries, validate schema cell counts, and exercise DMA clients for memory/peripheral interface selection and peripheral ID decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/at91.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/axi-dmac.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/axi-dmac.h

## Purpose
Defines bus-type constants for Analog Devices AXI DMAC bindings. The long comment describes whether the source and destination bus type cells are meaningful for different compatible strings and directions.

## Important APIs, Types, and Constants
Exports `AXI_DMAC_BUS_TYPE_AXI_MM` 0, `AXI_DMAC_BUS_TYPE_AXI_STREAM` 1, and `AXI_DMAC_BUS_TYPE_FIFO` 2. These constants encode memory-mapped AXI, AXI Stream, and FIFO endpoints.

## Control Flow and State
No executable flow. Runtime DMA transfer routing is configured by the AXI DMAC driver after parsing DT cells.

## Dependencies and Integration Points
Self-contained header used by AXI DMAC controller nodes and DMA client/device-tree descriptions that specify endpoint bus types.

## Risks and Test Signals
The risk is semantic mismatch between compatible string and bus type cells. Tests include `dtbs_check`, DTS compile coverage for memory-to-stream and stream-to-memory designs, and runtime DMA transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/axi-dmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/dw-dmac.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/dw-dmac.h

## Purpose
Defines DesignWare DMAC AHB HPROT flag bits for DT configuration.

## Important APIs, Types, and Constants
Exports `DW_DMAC_HPROT1_PRIVILEGED_MODE`, `DW_DMAC_HPROT2_BUFFERABLE`, and `DW_DMAC_HPROT3_CACHEABLE`, corresponding to bits 0, 1, and 2. These are bit flags that may be ORed.

## Control Flow and State
No control flow. The DesignWare DMA driver interprets these flags when programming transfer protection/cache attributes.

## Dependencies and Integration Points
Self-contained binding used by DT DMA controller configuration and potentially DMA client properties.

## Risks and Test Signals
Incorrect flag composition can affect security attributes, buffering, or cacheability. Test signals include DT schema validation and DMA transfer tests on platforms using privileged, bufferable, or cacheable modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/dw-dmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/fsl-edma.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/fsl-edma.h

## Purpose
Defines Freescale/NXP eDMA DT flag bits used in DMA specifiers.

## Important APIs, Types, and Constants
Exports `FSL_EDMA_RX`, `FSL_EDMA_REMOTE`, `FSL_EDMA_MULTI_FIFO`, `FSL_EDMA_EVEN_CH`, and `FSL_EDMA_ODD_CH`, with bit values from `0x1` through `0x10`. They encode direction, remote request usage, multi-FIFO behavior, and channel parity restrictions.

## Control Flow and State
No runtime flow. The flags are compile-time bitmasks; transfer state is in the eDMA engine and driver.

## Dependencies and Integration Points
Self-contained header included by DTS files that configure eDMA request cells and by drivers or examples that interpret those cells.

## Risks and Test Signals
Because these are flags, consumers must OR values rather than treat them as exclusive enums. Test signals include schema validation and DMA client tests for RX/TX, remote requests, multi-FIFO, and even/odd channel constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/fsl-edma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/jz4780-dma.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/jz4780-dma.h

## Purpose
Defines Ingenic JZ4780 DMA request IDs for device-tree DMA specifiers.

## Important APIs, Types, and Constants
Exports `JZ4780_DMA_*` constants for I2S, automatic DMA, SADC, UARTs, SSI, MSC, PCM, SMBus/I2C-style controllers, and DES engine TX/RX. Values are hardware request indexes, spanning from `0x4` through `0x2f`.

## Control Flow and State
No control flow. DMA channel allocation and request routing are handled by the Ingenic DMA driver.

## Dependencies and Integration Points
Self-contained header used by JZ4780 DTS device nodes in `dmas` properties and by the DMA provider mapping table.

## Risks and Test Signals
Wrong request IDs route transfers to the wrong peripheral. Test signals include DTS compilation, schema validation, and runtime DMA tests for audio, serial, storage, and crypto peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/jz4780-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/nbpfaxi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/nbpfaxi.h

## Purpose
Defines NBPF AXI DMA slave request mode flags for DT bindings.

## Important APIs, Types, and Constants
Exports `NBPF_SLAVE_RQ_HIGH`, `NBPF_SLAVE_RQ_LOW`, and `NBPF_SLAVE_RQ_LEVEL` with bit values 1, 2, and 4. These describe active-high, active-low, and level-sensitive request semantics.

## Control Flow and State
No runtime flow. The DMA driver uses the flags when configuring handshake behavior.

## Dependencies and Integration Points
Self-contained binding included by DT nodes using the NBPF AXI DMA controller.

## Risks and Test Signals
Incorrect polarity or level configuration can prevent DMA requests or cause repeated service. Test signals include schema validation and peripheral DMA tests that verify handshake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/nbpfaxi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/qcom-gpi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/qcom-gpi.h

## Purpose
Defines Qualcomm GPI DMA protocol IDs for DT bindings.

## Important APIs, Types, and Constants
Exports `QCOM_GPI_SPI` 1, `QCOM_GPI_UART` 2, and `QCOM_GPI_I2C` 3. These values identify the peripheral protocol used by a GPI DMA channel.

## Control Flow and State
No local flow or state. Runtime protocol handling is implemented by the Qualcomm GPI DMA driver and firmware/hardware.

## Dependencies and Integration Points
Self-contained header included by Qualcomm DTS files for SPI, UART, and I2C DMA channel configuration.

## Risks and Test Signals
Wrong protocol ID can make the DMA engine interpret descriptors incorrectly. Test signals include DT schema validation and DMA-backed SPI, UART, and I2C transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/qcom-gpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/sun4i-a10.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/sun4i-a10.h

## Purpose
Defines Allwinner sun4i A10 DMA endpoint class constants. The header comment explains the two hardware channel categories.

## Important APIs, Types, and Constants
Exports `SUN4I_DMA_NORMAL` 0 and `SUN4I_DMA_DEDICATED` 1. Normal DMA channels handle memory-to-memory and some simple peripheral cases; dedicated channels cover broader peripheral use as described by the binding.

## Control Flow and State
No executable flow. Runtime allocation and transfer state live in the sun4i DMA controller driver.

## Dependencies and Integration Points
Self-contained header used by sun4i DT DMA specifiers and controller/client nodes.

## Risks and Test Signals
Using the wrong channel class can make a client request unsupported hardware resources. Test signals include schema validation and DMA client tests for peripherals that require normal versus dedicated channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/sun4i-a10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/x1000-dma.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/x1000-dma.h

## Purpose
Defines Ingenic X1000 DMA request IDs for device-tree DMA specifiers.

## Important APIs, Types, and Constants
Exports `X1000_DMA_*` request constants for DMIC, I2S, automatic DMA, UARTs, SSI, MSC, PCM, and SMB controllers. Values are sparse hardware request numbers, from `0x5` through `0x29`.

## Control Flow and State
No runtime flow. The Ingenic DMA provider maps these request IDs to hardware DMA request lines.

## Dependencies and Integration Points
Self-contained header used by X1000 DTS nodes in `dmas` cells and by the matching DMA driver.

## Risks and Test Signals
Sparse request IDs should not be renumbered or compacted. Tests include DTS build, schema validation, and runtime DMA transfers for audio, serial, storage, and SMB controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/x1000-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/x1830-dma.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/x1830-dma.h

## Purpose
Defines Ingenic X1830 DMA request IDs for DT consumers.

## Important APIs, Types, and Constants
Exports `X1830_DMA_*` constants for I2S, automatic DMA, SADC, UARTs, SSI, MSC, DMIC, SMB, and DES TX/RX. Numeric values range from `0x6` through `0x2f` and are intentionally sparse.

## Control Flow and State
No runtime logic. DMA request routing and channel state are implemented by the Ingenic DMA driver.

## Dependencies and Integration Points
Self-contained binding included by X1830 DTS files and consumed by the DMA provider through `dmas` specifiers.

## Risks and Test Signals
Wrong request values route channels incorrectly. Test signals include schema validation and runtime DMA transfer coverage for serial, audio, storage, ADC, SMB, and DES users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/x1830-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/xlnx-zynqmp-dpdma.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/dma/xlnx-zynqmp-dpdma.h

## Purpose
Defines Xilinx ZynqMP DisplayPort DMA channel IDs.

## Important APIs, Types, and Constants
Exports `ZYNQMP_DPDMA_VIDEO0`, `VIDEO1`, `VIDEO2`, `GRAPHICS`, `AUDIO0`, and `AUDIO1`, numbered 0 through 5. These are channel indexes for display pipeline layers and audio streams.

## Control Flow and State
No local control flow. Runtime transfer state belongs to the ZynqMP DPDMA driver.

## Dependencies and Integration Points
Self-contained header used by ZynqMP display/audio DT nodes that reference DPDMA channels.

## Risks and Test Signals
Channel swaps can corrupt displayed layers or audio routing. Test signals include DT schema validation and display pipeline tests for video, graphics overlay, and audio channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/dma/xlnx-zynqmp-dpdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/firmware/imx/rsrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/firmware/imx/rsrc.h

## Purpose
Defines NXP i.MX System Controller resource and control IDs for firmware-mediated DT bindings. The file explicitly states that resource list items should never be changed or removed and only added at the end, making it a strict firmware/DT ABI.

## Important APIs, Types, and Constants
The main namespace is `IMX_SC_R_*`, covering application processors, display controllers, V2X, DMA channels, UART/SPI/I2C, ADC, FTM, CAN, GPU partitions, PCIe, SATA, SERDES, LCD, PWM, GPIO, MU, OCRAM, audio, MIPI, CSI, HDMI, VPU, DC resources, pads, and board resources. `IMX_SC_R_CAN(x)` is a function-like convenience macro over `IMX_SC_R_CAN_0`. The later `IMX_SC_C_*` constants define control IDs such as clock, reset, power, timing, link, PHY, MISC, and `IMX_SC_C_LAST`.

## Control Flow and State
No runtime flow exists in the header. Resource ownership, power state, clocks, resets, and controls are persisted or enforced by the i.MX system controller firmware; the kernel passes these IDs across firmware calls.

## Dependencies and Integration Points
Self-contained binding used by i.MX DT nodes and firmware clients that communicate with SCU/SCFW services. It integrates with power-domain, clock, reset, pin, and resource-management drivers.

## Risks and Test Signals
Risk is very high because values cross firmware and partition boundaries. Removing, reordering, or reusing IDs can break power/resource ownership or secure partitioning. Test signals include DT compilation, firmware API compatibility checks, boot on SCFW-based i.MX platforms, and runtime tests for resource allocation, power domains, clocks, resets, and peripheral access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/firmware/imx/rsrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/firmware/qcom,scm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/firmware/qcom,scm.h

## Purpose
Defines Qualcomm SCM VMID constants for secure monitor and memory ownership bindings.

## Important APIs, Types, and Constants
Exports `QCOM_SCM_VMID_*` macros for trust zone, HLOS, sensor/ADSP/CDSP/MDSP subsystems, secure display/camera/video, hypervisor, WLAN, SPSS, NAV, TVM, and OEMVM IDs. Values are sparse hexadecimal VM identifiers from `0x1` through `0x31`.

## Control Flow and State
No local flow. Runtime state is in Qualcomm secure firmware/hypervisor memory protection tables; these IDs identify VM owners in SCM calls or DT properties.

## Dependencies and Integration Points
Self-contained binding used by Qualcomm firmware, memory protection, reserved-memory, and SCM-related DT descriptions.

## Risks and Test Signals
Wrong VMID values are security-sensitive and can assign memory or device access to the wrong execution environment. Test signals include DT schema validation, SCM call success, memory assignment tests, and secure subsystem boot validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/firmware/qcom,scm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mediatek,mt6795-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mediatek,mt6795-gce.h

## Purpose
Defines MediaTek MT6795 GCE/CMDQ priorities and hardware event IDs for command queue synchronization.

## Important APIs, Types, and Constants
Exports thread priority constants from `CMDQ_THR_PRIO_LOWEST` through `CMDQ_THR_PRIO_HIGHEST` and a large `CMDQ_EVENT_*` set for mutex stream EOF, display blocks, MDP, ISP, camera, sensor FIFO, JPEG encode/decode, and related events. Event values are sparse and extend to JPEG events around 257-259.

## Control Flow and State
No executable flow. Runtime command execution, waits, and event signaling are handled by GCE hardware and the CMDQ driver.

## Dependencies and Integration Points
Self-contained header used by MT6795 DT nodes and MediaTek display/media drivers that submit CMDQ packets with event waits.

## Risks and Test Signals
Event IDs are synchronization ABI. Wrong values can deadlock command queues or signal completion early. Test signals include DT schema validation and runtime display/camera/JPEG pipelines using CMDQ waits and triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mediatek,mt6795-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8173-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8173-gce.h

## Purpose
Defines MT8173 GCE/CMDQ thread priorities, subsystem codes, and display event IDs.

## Important APIs, Types, and Constants
Exports `CMDQ_THR_PRIO_LOWEST` and `CMDQ_THR_PRIO_HIGHEST`, `SUBSYS_1400XXXX` through `SUBSYS_1402XXXX`, and display events such as OVL/RDMA/WDMA/COLOR SOF, mutex stream EOF, and RDMA underrun events.

## Control Flow and State
No runtime logic. CMDQ packets and waits are interpreted by the MediaTek GCE driver and hardware.

## Dependencies and Integration Points
Self-contained DT binding used by MT8173 display subsystem nodes and CMDQ-aware drivers.

## Risks and Test Signals
Wrong subsystem or event IDs can make register access or synchronization target the wrong block. Test signals include DT schema validation and display pipeline testing under vblank, mutex EOF, and underrun conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8173-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8183-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8183-gce.h

## Purpose
Defines MT8183 GCE/CMDQ timeout, priority, subsystem, and event constants for display, image, video, camera, and IPU synchronization.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT` as `0xffffffff`, priority constants, subsystem address-window IDs, and `CMDQ_EVENT_*` values for display mutex/vblank/stream EOF, MDP, ISP, camera, VENC/VDEC, and IPU done signals. Values are sparse and include high IPU event ranges.

## Control Flow and State
No control flow. The constants drive command queue packet behavior at runtime, but state is in GCE threads, event registers, and driver-managed packets.

## Dependencies and Integration Points
Self-contained header included by MediaTek MT8183 DTs and CMDQ client drivers for display/media pipelines.

## Risks and Test Signals
Timeout constants and event IDs directly affect synchronization. Misnumbering can cause timeouts, hangs, or data corruption in media pipelines. Test signals include DT checks and runtime tests for display, MDP, camera, video codec, and IPU workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8183-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8186-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8186-gce.h

## Purpose
Defines MT8186 GCE/CMDQ command constants for priorities, CPR count, subsystem routing, GPR registers, hardware events, software tokens, timer tokens, and event maximums.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT`, `CMDQ_TIMEOUT_DEFAULT`, eight priority levels, `GCE_CPR_COUNT`, `SUBSYS_*` address-window IDs, `GCE_GPR_R00` through `R15`, numerous `CMDQ_EVENT_*` IDs, `CMDQ_TOKEN_*` software synchronization tokens, and `CMDQ_EVENT_MAX` `0x3FF`.

## Control Flow and State
No executable code. Runtime state is the GCE command queue thread state, event flags, GPR registers, and software token state managed by the CMDQ driver.

## Dependencies and Integration Points
Self-contained binding used by MT8186 DT nodes and MediaTek display/media/camera drivers that use CMDQ synchronization.

## Risks and Test Signals
Event and token namespaces must not collide. `CMDQ_EVENT_MAX` constrains valid hardware event IDs. Test signals include DT validation plus runtime CMDQ workloads across display, MDP, camera, video, and token/timer waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8186-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8192-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8192-gce.h

## Purpose
Defines MT8192 GCE/CMDQ constants for command priorities, timeout behavior, subsystem routing, GPR registers, display/media/camera events, buffer underrun events, and maximum event count.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT`, `CMDQ_TIMEOUT_DEFAULT`, priority levels 0-7, `SUBSYS_*` IDs, `GCE_GPR_R00`-`R15`, and `CMDQ_EVENT_*` IDs ending with underrun events and `CMDQ_MAX_HW_EVENT` 512.

## Control Flow and State
No local flow. GCE runtime state is managed by hardware threads and the CMDQ driver, which consume these IDs in packet waits/signals.

## Dependencies and Integration Points
Self-contained binding included by MT8192 DT and MediaTek CMDQ clients, especially display, MDP, imaging, and video pipelines.

## Risks and Test Signals
Events are synchronization points; bad IDs create hangs or early completions. The max-event value should remain consistent with hardware and driver bitmaps. Test with DT schema checks and runtime pipelines that exercise vblank, frame done, underrun, and media completion events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8192-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8195-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8195-gce.h

## Purpose
Defines the large MT8195 GCE/CMDQ binding surface: timeout constants, thread priorities, CPR register count, subsystem windows, GPR registers, and hundreds of hardware event IDs for imaging, display, video, HDMI, DP, WPE, and software output pins.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT`, `CMDQ_TIMEOUT_DEFAULT`, `CMDQ_THR_PRIO_*`, `GCE_CPR_COUNT` 1312, `SUBSYS_*`, `GCE_GPR_R00` through `R15`, and `CMDQ_EVENT_*` IDs. The event namespace reaches `CMDQ_EVENT_OUTPIN_1` 1019 and defines `CMDQ_MAX_HW_EVENT` 1019.

## Control Flow and State
No executable flow in the header. Runtime state is in GCE event registers, command queue threads, GPR/CPR registers, and CMDQ driver packet state.

## Dependencies and Integration Points
Self-contained binding used by MT8195 DT nodes and high-level MediaTek display, camera, video, and image-processing drivers that synchronize work through CMDQ.

## Risks and Test Signals
The breadth of event IDs creates high collision and stale-ID risk. Max-event handling must match driver allocation sizes. Test signals include DT validation, CMDQ packet tests, and end-to-end display, camera, video codec, HDMI/DP, and WPE pipeline tests under completion and timeout scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8195-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic,t7-periphs-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic,t7-periphs-pinctrl.h

## Purpose
Defines Amlogic T7 peripheral GPIO pin numbers for DT pinctrl/GPIO bindings.

## Important APIs, Types, and Constants
Exports banked pin macros such as `GPIOB_*`, `GPIOC_*`, `GPIOD_*`, `GPIOE_*`, `GPIOF_*`, `GPIOG_*`, `GPIOH_*`, and `GPIO_TEST_N`. Values are linear pin indexes from 0 through 156 across the peripheral pin controller.

## Control Flow and State
No runtime flow. GPIO direction, mux, pull, and value state are managed by the Amlogic pinctrl/GPIO driver.

## Dependencies and Integration Points
Self-contained binding included by T7 DTS pinctrl groups and GPIO consumers. It integrates with pin controller nodes that expect these numeric offsets.

## Risks and Test Signals
Bank ordering and pin numbers must match hardware and driver offset tables. Wrong constants can mux or toggle the wrong pin. Test signals include DTS compilation, pinctrl schema validation, and board-level tests for GPIO, pinmux, interrupts, and peripheral pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic,t7-periphs-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic-c3-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic-c3-gpio.h

## Purpose
Defines Amlogic C3 GPIO pin numbers for DT pinctrl and GPIO consumers.

## Important APIs, Types, and Constants
Exports banked macros `GPIOE_*`, `GPIOB_*`, `GPIOX_*`, `GPIOD_*`, `GPIOA_*`, and `GPIO_TEST_N`, numbered from 0 through 54. The constants are linear offsets into the C3 GPIO controller.

## Control Flow and State
No executable logic. Runtime pin state is controlled by the Amlogic C3 pinctrl/GPIO driver and hardware registers.

## Dependencies and Integration Points
Self-contained header included by Amlogic C3 DTS files for GPIO specifiers, pin mux groups, and interrupt-capable pins.

## Risks and Test Signals
The primary risk is bank/offset mismatch, which can drive the wrong external signal. Test signals include DT schema validation, GPIO line naming/offset checks, and board-level tests for pinmux, GPIO input/output, and interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/amlogic-c3-gpio.h -->
