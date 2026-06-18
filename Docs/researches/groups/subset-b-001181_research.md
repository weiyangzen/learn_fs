# subset-b-001181

Grouped research for Allwinner sunxi-ng and legacy sunxi clock-controller files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.c

## Purpose
This is the sunxi-ng CCU provider for Allwinner V3 and V3s SoCs. It describes PLLs, CPU/AXI/AHB/APB roots, bus gates, MMC clocks and phases, USB, DRAM, display, CSI, VE, audio, MBUS, and reset lines, then registers the block as a CCF and reset-controller provider.

## Important APIs, Types, And Functions
Important descriptors include `pll_cpu_clk`, SDM-backed `pll_audio_base_clk`, fractional `pll_video_clk`, `pll_ve_clk`, `pll_isp_clk`, DDR and peripheral PLLs, CPU/AHB/APB mux/dividers, many `SUNXI_CCU_GATE` bus clocks, `SUNXI_CCU_MP_WITH_MUX_GATE` MMC/SPI/CE module clocks, `SUNXI_CCU_PHASE` MMC sample/output clocks, onecell tables for V3 and V3s, reset maps, and `sun8i_v3s_ccu_probe()`.

## Control Flow
Probe selects the descriptor from OF match data, maps MMIO, forces the PLL-audio 1x divider to 1 for SDM operation, forces DE and TCON parents to the video PLL so display units share a parent, then calls `devm_sunxi_ccu_probe()`. Runtime CCF operations are table-driven by the common sunxi-ng helpers.

## State And Persistence
No filesystem state is stored. Boot state consists of probe-time register fixups plus subsequent hardware register changes from clock and reset consumers. CPU, DRAM, and MBUS clocks are marked critical where disabling would destabilize the system.

## Dependencies And Integration Points
The driver depends on sunxi-ng helpers, V3s clock/reset dt-bindings, Linux platform and OF APIs, and external oscillator parents. It integrates with MMC, CE, SPI, USB host/PHY, EMAC/ePHY, UART/I2C, codec/I2S, display/TCON/DE, CSI/MIPI CSI, VE, DRAM, and MBUS consumers.

## Risks
Descriptor correctness is the main risk: V3 and V3s share most hardware but expose different I2S/reset IDs. Audio SDM uses fixed supported rates and forced dividers. DE/TCON parent fixups are required for display operation. Mistyped bit positions can affect adjacent bus gates or reset lines.

## Test Signals
Test by booting V3 and V3s DTs, checking probe success and clock-summary entries, validating CPU rate changes, audio 22.5792/24.576 MHz paths, MMC phases and transfers, USB host/PHY, EMAC/ePHY, UART/I2C/SPI, display pipeline, CSI, VE, and reset-controller toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.h

## Purpose
This private header defines internal clock indices for the V3/V3s CCU descriptor and includes public dt-binding IDs for clocks and resets.

## Important APIs, Types, And Functions
It declares non-exported IDs such as `CLK_PLL_CPU`, `CLK_PLL_AUDIO_BASE`, `CLK_AXI`, `CLK_AHB1`, `CLK_APB1`, `CLK_APB2`, `CLK_AHB2`, `CLK_DRAM`, `CLK_MBUS`, and `CLK_PLL_DDR1`. Publicly exported bus and module clock IDs are provided by `dt-bindings/clock/sun8i-v3s-ccu.h`; reset IDs come from the matching reset binding.

## Control Flow
The header has no runtime control flow. It is consumed at compile time by `ccu-sun8i-v3s.c` to size and index `clk_hw_onecell_data` arrays.

## State And Persistence
It stores no state. The numeric constants are ABI-sensitive within the provider tables because device-tree clock specifiers index the same onecell array.

## Dependencies And Integration Points
Dependencies are the dt-binding headers and the C compiler. Integration is direct with the V3/V3s provider and indirect with all DT consumers using exported IDs.

## Risks
Changing numbers can break device-tree ABI or point consumers at the wrong `clk_hw`. Reserved holes document clocks that are not implemented or not exported and should not be compacted casually.

## Test Signals
Build coverage plus DT boot tests are the main signals. Clock-summary names should line up with the binding IDs used by MMC, display, audio, USB, and bus consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.c

## Purpose
This provider models the separate A80 Display Engine CCU block. It exposes front-end/back-end engine gates, IEP DEU/DRC gates, merge clock, DRAM and bus gates, simple dividers, and display-engine reset controls.

## Important APIs, Types, And Functions
Key objects are the FE/BE/IEP/merge `SUNXI_CCU_GATE` descriptors, DRAM gates, bus gates, `fe*_div_clk` and `be*_div_clk` dividers, `sun9i_a80_de_hw_clks`, `sun9i_a80_de_resets`, `sun9i_a80_de_clk_desc`, and `sun9i_a80_de_clk_probe()`.

## Control Flow
Probe maps the DE CCU registers, obtains the parent bus clock and external reset control, enables the bus clock so registers can be accessed, deasserts reset, and registers the CCU. On registration failure it reasserts reset and disables the bus clock.

## State And Persistence
No persistent software state exists. The bus clock remains prepared/enabled after successful probe because the provider must keep register access live. Reset and gate states are hardware register state managed through CCF and reset-controller calls.

## Dependencies And Integration Points
It depends on sunxi-ng common/gate/div/reset helpers, platform devices, parent `bus`, reset controller infrastructure, and A80 DE dt-bindings. It integrates with the DRM/display-engine pipeline, FE/BE blocks, IEP post-processing, DRAM channels, and bus fabric.

## Risks
The provider is sensitive to probe ordering and external reset/bus resources. If the bus clock is disabled too early, subsequent clock/reset accesses can fault or hang. Divider IDs are internal but still must fit the onecell size. Gate bit mistakes can stall only one display engine sub-block.

## Test Signals
Test signals include successful `allwinner,sun9i-a80-de-clks` probe, no bus/reset acquisition errors, visible DE clocks in clk-summary, display pipeline bring-up across FE/BE/IEP paths, and reset operations for FE, BE, DEU, DRC, and merge blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.h

## Purpose
This private header sizes the A80 Display Engine CCU onecell clock table and reserves IDs for internal FE/BE divider clocks.

## Important APIs, Types, And Functions
It includes `dt-bindings/clock/sun9i-a80-de.h` and `dt-bindings/reset/sun9i-a80-de.h`, then defines `CLK_FE0_DIV` through `CLK_BE2_DIV` and `CLK_NUMBER`.

## Control Flow
There is no runtime flow; the C provider uses these constants for array initializers and provider size.

## State And Persistence
No mutable state is present. The constants are compile-time table indexes and must remain aligned with `ccu-sun9i-a80-de.c`.

## Dependencies And Integration Points
It integrates with the DE clock provider and the public binding IDs consumed by the display subsystem.

## Risks
Risk is low but ABI-adjacent: adding internal clocks below public IDs or changing `CLK_NUMBER` incorrectly can make onecell lookups fail or expose null clocks.

## Test Signals
Build and probe coverage are sufficient, with clk-summary confirming divider clocks exist only as provider internals used by FE/BE gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.c

## Purpose
This provider models the A80 USB CCU block. It exposes bus gates for HCI controllers, OHCI functional gates, USB PHY/HSIC gates, and reset lines for HCI and PHY/HSIC domains.

## Important APIs, Types, And Functions
Important data includes firmware parent arrays for `hosc` and `bus`, gate descriptors such as `bus_hci0_clk`, `usb_ohci0_clk`, `usb0_phy_clk`, `usb1_hsic_clk`, `usb_hsic_clk`, the onecell clock table, reset map, descriptor, and `sun9i_a80_usb_clk_probe()`.

## Control Flow
Probe maps registers, obtains and enables the `bus` clock to access the USB CCU registers, then registers the CCU with `devm_sunxi_ccu_probe()`. On failure it disables the bus clock.

## State And Persistence
The driver has no persistent state beyond live hardware gates and resets. The bus clock remains enabled after successful probe to keep this secondary CCU accessible.

## Dependencies And Integration Points
Dependencies are sunxi-ng common/gate/reset helpers, Linux platform/clock APIs, A80 USB bindings, and firmware-named parents. It integrates with EHCI/OHCI/HCI controllers, USB PHYs, HSIC PHYs, and reset-controller consumers.

## Risks
Main risks are parent naming and register access ordering. If the `bus` clock is unavailable or disabled, the provider cannot safely touch registers. HCI and PHY reset bits share compact registers, so bit mistakes can break multiple ports.

## Test Signals
Test by probing `allwinner,sun9i-a80-usb-clks`, checking clk-summary for HCI/OHCI/PHY/HSIC clocks, enumerating USB devices on all ports, validating HSIC if present, and exercising reset lines during controller probe and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.h

## Purpose
This header binds the A80 USB CCU C file to its public clock and reset dt-bindings and defines the onecell array size.

## Important APIs, Types, And Functions
It includes `sun9i-a80-usb.h` clock/reset binding headers and defines `CLK_NUMBER` as `CLK_USB_HSIC + 1`.

## Control Flow
It has no runtime flow. The provider uses the constant to size `sun9i_a80_usb_hw_clks`.

## State And Persistence
No state is stored. The value is a compile-time contract between binding IDs and onecell provider sizing.

## Dependencies And Integration Points
It integrates with `ccu-sun9i-a80-usb.c` and DT consumers of USB HCI, OHCI, PHY, and HSIC clocks/resets.

## Risks
Incorrect sizing can truncate the last clock ID or leave lookup holes, causing `of_clk_get()` failures for USB consumers.

## Test Signals
Build and USB controller probe tests validate that all exported IDs resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.c

## Purpose
This is the main sunxi-ng CCU provider for Allwinner A80. It describes cluster CPU PLLs and muxes, audio/peripheral/video/GPU/DE/ISP PLLs, bus roots, module clocks, MMC phases, display/media clocks, extensive bus gates, and reset lines.

## Important APIs, Types, And Functions
Important APIs and data include `CCU_SUN9I_LOCK_REG`, CPU PLL `ccu_mult` descriptors with shared lock register bits, `pll_audio_clk`, many `ccu_nkmp` PLL descriptors, CPU/AHB/APB dividers and muxes, module gates/dividers for NAND/MMC/SPI/I2S/display/CSI/GPU/SATA, `sun9i_a80_hw_clks`, `sun9i_a80_ccu_resets`, `sun9i_a80_cpu_pll_fixup()`, and `sun9i_a80_ccu_probe()`.

## Control Flow
Probe maps registers, clears unsupported audio PLL d1/d2 divider usage, fixes both CPU cluster PLLs by clearing P and restoring N when needed, then calls `devm_sunxi_ccu_probe()`. Runtime operation is descriptor-driven through shared sunxi-ng CCF and reset helpers.

## State And Persistence
State is entirely hardware register state for this boot. Probe mutates PLL registers before registration. Critical flags protect CPU muxes, GT bus, CCI400, and SDRAM paths from accidental disable.

## Dependencies And Integration Points
Dependencies include sunxi-ng common helpers, A80 clock/reset dt-bindings, OF/platform APIs, and oscillator parents. Integration spans CPU clusters, interconnect, CCI400, NAND, MMC, TS, security engine, SPI, audio, SDRAM, DE/LCD/MIPI/HDMI/CSI, VE, GPU, SATA, GMAC/USB bus gates, GPIO/PIO, I2C, UART, message box, spinlock, and reset consumers.

## Risks
Risk is high because this file is large and register dense. CPU PLLs are approximated as multipliers with P forced to /1; audio PLL d1/d2 are forcibly cleared; several mux tables use sparse hardware selector values. Duplicate or wrong array entries, bit offsets, or lock bits can silently misroute clocks or reset unrelated blocks.

## Test Signals
Test with A80 boot, successful `allwinner,sun9i-a80-ccu` probe, clock-summary inspection, CPU cluster rate changes, MMC with phase tuning, NAND/SPI/I2C/UART, audio sample rates, display and HDMI, CSI, VE, GPU, SATA/GMAC/USB bus clients, reset-controller operations, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.h

## Purpose
This private header defines A80 main CCU internal clock IDs that are not fully covered by public dt-bindings and sets the onecell table size.

## Important APIs, Types, And Functions
It includes A80 clock/reset binding headers and defines IDs for CPU PLLs, private PLLs, CPU/bus roots, `CLK_ATS`, `CLK_TRACE`, and `CLK_NUMBER`.

## Control Flow
There is no runtime flow. The constants are consumed by `ccu-sun9i-a80.c` array initializers.

## State And Persistence
No state is stored. Numeric identity is the important contract because DT consumers index the onecell provider by ID.

## Dependencies And Integration Points
Integration is with the main A80 CCU provider and all downstream clock/reset consumers.

## Risks
Changing constants can break ABI or misalign provider arrays. Comments marking exported groups should be preserved to avoid renumbering internal holes.

## Test Signals
Build and A80 DT boot tests should confirm all public binding IDs resolve and no clock lookups return unexpected nulls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.c

## Purpose
This is the sunxi-ng CCU provider for the Allwinner suniv F1C100s/F1C200s family. It describes CPU, audio, video, VE, DDR, peripheral PLLs, bus roots, module gates, MMC phases, IR/audio/display/camera/video clocks, DRAM gates, resets, and probe registration.

## Important APIs, Types, And Functions
Important descriptors include `pll_cpu_clk`, audio/video/VE/DDR/peripheral PLLs, CPU/AHB/APB mux/dividers, bus gates for DMA/MMC/DRAM/SPI/USB/display/camera/audio/I2C/UART, MMC MP clocks and sample/output phases, audio muxes, IR MP clock, display/TV/CSI/VE/codec/AVS gates, `suniv_hw_clks`, reset maps, `suniv_pll_cpu_nb`, `suniv_cpu_nb`, and `suniv_f1c100s_ccu_probe()`.

## Control Flow
Probe maps the CCU resource, registers all clocks/resets through `devm_sunxi_ccu_probe()`, then registers a CPU mux notifier and PLL notifier so CPU consumers temporarily switch away during PLL CPU rate changes and the PLL is reset after rate changes.

## State And Persistence
State is hardware register state plus notifier registration for the boot. CPU clocking is protected by notifier sequencing; PLL/audio fixed-factor clocks are CCF objects without storage beyond registration.

## Dependencies And Integration Points
Dependencies include sunxi-ng helpers, suniv dt-bindings, platform/OF APIs, and oscillator parents. It integrates with CPUfreq, MMC, SPI, USB OTG, display engine/TCON/TV, CSI/TVD/TVE, audio codec/I2S/SPDIF, IR, I2C/UART, DRAM clients, VE, and reset-controller users.

## Risks
Notifier order is important for safe CPU PLL changes. Display/video mux tables use sparse values. The small SoC has many unrelated gates packed into few registers, so bit mistakes have broad effects. Audio fixed factors are intentionally arranged for supported clocking and should not be renamed casually.

## Test Signals
Test signals include successful F1C100s/F1C200s boot, clk-summary coverage, CPU rate changes without lockups, MMC transfer and phase changes, USB OTG, SPI/I2C/UART, audio playback/capture, display/TV output, camera paths, VE, DRAM gates, and reset toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.h

## Purpose
This private header defines internal clock indices for the suniv F1C100s CCU provider and includes public clock/reset bindings.

## Important APIs, Types, And Functions
It maps internal PLL and bus-root IDs such as `CLK_PLL_CPU`, `CLK_PLL_AUDIO_BASE`, `CLK_CPU`, `CLK_AHB`, `CLK_APB`, `CLK_DRAM`, and `CLK_PLL_VIDEO_2X`; exported module and bus IDs come from the dt-binding header.

## Control Flow
There is no runtime flow. The C provider uses the constants to populate `clk_hw_onecell_data`.

## State And Persistence
No mutable state exists. The numeric layout must remain consistent with the provider and binding IDs.

## Dependencies And Integration Points
Integration is with `ccu-suniv-f1c100s.c` and device-tree consumers for the small suniv SoC family.

## Risks
Renumbering can break DT clock specifiers or cause wrong hardware to be controlled. Reserved/exported ranges need to remain aligned with public bindings.

## Test Signals
Build coverage and suniv boot with successful clock lookups validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.c

## Purpose
`ccu_common.c` is the registration and shared utility layer for sunxi-ng clock controller providers. It wires descriptor arrays into Linux CCF, registers reset controllers, provides PLL lock waiting, rate comparison policy, and PLL notifier support.

## Important APIs, Types, And Functions
Important APIs are `ccu_helper_wait_for_lock()`, `ccu_is_better_rate()`, `ccu_pll_notifier_register()`, `devm_sunxi_ccu_probe()`, and `of_sunxi_ccu_probe()`. Internally `sunxi_ccu_probe()` initializes shared locks/base pointers, registers each `clk_hw`, installs the onecell provider, and registers `ccu_reset_ops`.

## Control Flow
Probe-style callers pass a mapped register base and `sunxi_ccu_desc`. The helper sets each `ccu_common` base/lock, registers clock hardware, applies rate ranges, adds the OF provider, then registers reset controls. Managed probe stores a release callback that unregisters resets, provider, and clocks.

## State And Persistence
It stores a small `struct sunxi_ccu` allocation for descriptor, spinlock, and reset-controller state during the provider lifetime. There is no disk persistence; hardware state is the register contents modified by the registered clocks/resets.

## Dependencies And Integration Points
Dependencies include CCF, OF providers, reset-controller core, iopoll, module support, and adjacent `ccu_gate`/`ccu_reset` helpers. Every sunxi-ng SoC CCU provider integrates through this file.

## Risks
Failure unwinding must unregister only clocks already registered. Lock wait timeouts warn but do not recover hardware. Rate comparison behavior affects every factor search, so closest-vs-not-above semantics must be changed cautiously.

## Test Signals
Test with builds for multiple sunxi-ng providers, probe/unbind where supported, reset-controller registration, clean failure injection if possible, and runtime checks that onecell clock lookups and reset operations work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.h

## Purpose
This header defines the common sunxi-ng descriptor state shared by all CCU clock classes and provider drivers.

## Important APIs, Types, And Functions
It declares feature flags such as `CCU_FEATURE_FRACTIONAL`, predivider/postdivider flags, lock-register, MMC timing, SDM, key-field, closest-rate, dual-div, and update-bit support. It defines `struct ccu_common`, `struct sunxi_ccu_desc`, `struct ccu_pll_nb`, conversion helpers, and exported common APIs.

## Control Flow
There is no runtime code except inline container conversion. The definitions drive compile-time construction of SoC clock descriptors and runtime behavior in class ops.

## State And Persistence
State fields include MMIO base, register offsets, rate limits, feature flags, a shared lock pointer, and embedded `clk_hw`. These are initialized by `ccu_common.c` during provider probe.

## Dependencies And Integration Points
Dependencies are Linux CCF/compiler headers and adjacent reset map declarations. Integration is universal across sunxi-ng gate, mux, divider, PLL, phase, SDM, and SoC provider files.

## Risks
Feature flag semantics are cross-cutting. Adding or changing bits can alter rate calculations, register writes, or locking behavior across many SoCs. `struct ccu_common` layout assumptions underpin all `container_of` conversions.

## Test Signals
Compile coverage plus multi-SoC boot/probe tests validate this header. Specific signals include correct rate limits, update-bit behavior, PLL lock waits, and MMC timing support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_div.c

## Purpose
`ccu_div.c` implements the sunxi-ng common-clock-framework operations for single-divider and mux-plus-divider clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It exports `ccu_div_ops` and uses `divider_determine_rate()`, `divider_recalc_rate()`, and `divider_get_val()` with optional fixed postdividers and mux predividers.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_div.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_div.h

## Purpose
This header declares the sunxi-ng divider clock class and the macros used by SoC descriptors to instantiate M, P, table, muxed, gated, closest-rate, and hardware-parent divider variants.

## Important APIs, Types, And Functions
Important types are `struct ccu_div_internal` and `struct ccu_div`; important macros include `_SUNXI_CCU_DIV*`, `SUNXI_CCU_DIV_TABLE*`, `SUNXI_CCU_M_WITH_MUX*`, `SUNXI_CCU_M_WITH_GATE`, `SUNXI_CCU_M_DATA_WITH_MUX*`, `SUNXI_CCU_M_HW_WITH_MUX_GATE`, and `SUNXI_CCU_P_DATA_WITH_MUX_GATE`.

## Control Flow
No runtime flow lives here. Macro expansion builds static descriptors consumed by `ccu_div_ops`.

## State And Persistence
Descriptor state covers enable bit, divider bitfield, optional mux, common register metadata, and fixed postdivider. Runtime mutation occurs in `ccu_div.c`.

## Dependencies And Integration Points
It depends on CCF, `ccu_common.h`, and `ccu_mux.h`; SoC CCU files depend on it heavily for bus and module clocks.

## Risks
Macro misuse can choose wrong flags, parent type API, offset semantics, or feature bits. Since these macros hide large initializers, review generated fields when adding new SoC clocks.

## Test Signals
Build coverage, clock registration, and rate-setting tests for muxed/table/fixed-postdivider clocks validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.c

## Purpose
`ccu_frac.c` provides helper functions for PLLs with two hardware fractional output selections. It is used by multiplier and N/M clock classes when a requested exact fractional rate is supported.

## Important APIs, Types, And Functions
Important APIs are `ccu_frac_helper_is_enabled()`, `enable()`, `disable()`, `has_rate()`, `read_rate()`, and `set_rate()`, all exported in the `SUNXI_CCU` namespace.

## Control Flow
Callers first check feature support, then either read the select bit to return one of two rates or update the select bit under the shared CCU spinlock. `set_rate()` waits for the PLL lock after changing selection.

## State And Persistence
No software state is persisted. The fractional enable and select bits in the PLL register are the only state.

## Dependencies And Integration Points
It depends on CCF for names/debug, MMIO access, spinlocks, and `ccu_common`. It integrates with `ccu_nm` and `ccu_mult` descriptors carrying `CCU_FEATURE_FRACTIONAL`.

## Risks
The enable bit is active-low in this helper, so inverted semantics are easy to break. Only two exact rates are supported; unsupported rates must return `-EINVAL` so normal factor search can proceed.

## Test Signals
Test by requesting known fractional video/VE/ISP/audio PLL rates and checking clk-summary/readback, plus validating non-fractional rates still disable fractional mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.h

## Purpose
This header defines the internal fractional-rate descriptor embedded in sunxi-ng PLL classes.

## Important APIs, Types, And Functions
It declares `struct ccu_frac_internal`, `_SUNXI_CCU_FRAC()`, and prototypes for the fractional helpers.

## Control Flow
There is no runtime flow here; it supplies descriptor data for `ccu_frac.c`.

## State And Persistence
State is limited to register bit masks and the two supported rates stored in static descriptors.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration is via `ccu_nm.h` and `ccu_mult.h` macros.

## Risks
The descriptor assumes exactly two fractional rates and active-low enable semantics implemented by the helper. Wrong masks can invert or misselect PLL frequencies.

## Test Signals
Build and exact-rate PLL tests validate that descriptors initialize correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.c

## Purpose
`ccu_gate.c` implements sunxi-ng gate clocks and reusable gate bit helpers for compound clock classes.

## Important APIs, Types, And Functions
Important APIs are `ccu_gate_helper_disable()`, `ccu_gate_helper_enable()`, `ccu_gate_helper_is_enabled()`, and exported `ccu_gate_ops`. The ops also support all-parent predivider rate propagation for gate-only derived clocks.

## Control Flow
Enable/disable/read paths update or read a single bit under the shared lock, optionally setting `CCU_SUNXI_UPDATE_BIT` before writes. Rate callbacks either pass through the parent rate or account for `CCU_FEATURE_ALL_PREDIV`.

## State And Persistence
Only hardware gate bits are state. No persistence or caching is used.

## Dependencies And Integration Points
It depends on CCF, MMIO, `ccu_common`, and is used by nearly every class and SoC provider for simple bus/module gates.

## Risks
A missing update bit can cause writes not to latch on some SoCs. A zero gate means always enabled, so callers must distinguish intentional zero from missing descriptor data.

## Test Signals
Test with clock prepare/enable/disable cycles, clk-summary gate state, and peripheral probe/suspend paths that rely on bus gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.h

## Purpose
This header declares the sunxi-ng gate clock class and constructor macros for string, hardware, firmware, parent-data, and predivided-parent variants.

## Important APIs, Types, And Functions
Important items are `struct ccu_gate`, `SUNXI_CCU_GATE*` macros, `hw_to_ccu_gate()`, helper prototypes, and `ccu_gate_ops`.

## Control Flow
No runtime flow is present. Macros expand to static descriptors consumed by `ccu_gate.c`.

## State And Persistence
Descriptor state includes enable mask, register offset, optional common predivider, feature flags, and embedded `clk_hw` init data.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration is broad across SoC descriptor tables and compound gate users.

## Risks
Choosing the wrong parent initializer flavor can break firmware-parent resolution. Predivider flags change reported rates for all consumers of that gate.

## Test Signals
Compile coverage and simple gate enable/readback tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mmc_timing.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mmc_timing.c

## Purpose
`ccu_mmc_timing.c` exposes a small platform API for switching supported MMC clocks between old and new timing modes.

## Important APIs, Types, And Functions
Important APIs are `sunxi_ccu_set_mmc_timing_mode()` and `sunxi_ccu_get_mmc_timing_mode()`, exported GPL symbols for MMC-related consumers.

## Control Flow
Both functions get the underlying `clk_hw`, convert to `ccu_common`, require `CCU_FEATURE_MMC_TIMING_SWITCH`, and then set or read `CCU_MMC_NEW_TIMING_MODE` in the clock register. The setter writes under the CCU spinlock.

## State And Persistence
The only state is the hardware timing-mode bit. No persistence exists across boot.

## Dependencies And Integration Points
It depends on Linux CCF internals, `linux/clk/sunxi-ng.h`, MMIO, and `ccu_common`. It integrates with MMC host drivers that need timing-mode control on newer Allwinner SoCs.

## Risks
Calling it on unsupported clocks returns `-ENOTSUPP`; consumers must handle that. The mode affects effective MMC clock rates and is coordinated with `ccu_mp_mmc_ops`, so inconsistent use can break card tuning.

## Test Signals
Test through MMC timing mode changes, card enumeration in legacy/high-speed modes, and clk-summary rates with old/new timing selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mmc_timing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.c

## Purpose
`ccu_mp.c` implements the sunxi-ng common-clock-framework operations for M/P divider clocks using either power-of-two P or dual linear dividers clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It also exports `ccu_mp_mmc_ops`, which wraps rates when `CCU_MMC_NEW_TIMING_MODE` halves MMC output.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.h

## Purpose
This header declares the M/P clock class used for many Allwinner module clocks, including the special MMC variant.

## Important APIs, Types, And Functions
Important items are `struct ccu_mp`, `SUNXI_CCU_MP_WITH_MUX_GATE*`, data/hardware parent variants, dual-divider variants, `SUNXI_CCU_MP_MMC_WITH_MUX_GATE`, `hw_to_ccu_mp()`, `ccu_mp_ops`, and `ccu_mp_mmc_ops`.

## Control Flow
It has no runtime flow; macros construct descriptors that `ccu_mp.c` operates on.

## State And Persistence
Descriptor state includes enable bit, M and P divider descriptors, mux metadata, optional fixed postdivider, and common feature flags.

## Dependencies And Integration Points
Dependencies are CCF, bitops, common/div/mult/mux headers. Integration is with MMC, SPI, NAND, IR, peripheral module clocks, and SoC CCU tables.

## Risks
Misusing dual-divider vs shift-style P changes the formula. MMC descriptors require `CLK_GET_RATE_NOCACHE` because timing mode changes the effective output outside normal CCF caching.

## Test Signals
Build and hardware tests for MMC, SPI, NAND, and other MP clocks validate macro correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.c

## Purpose
`ccu_mult.c` implements the sunxi-ng common-clock-framework operations for simple multiplier PLL clocks clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It supports optional fractional-rate helper use before falling back to integer multiplier programming and waits for lock bits after writes.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.h

## Purpose
This header declares the simple multiplier clock class used by CPU PLLs and similar clocks.

## Important APIs, Types, And Functions
It defines `struct ccu_mult_internal`, `_SUNXI_CCU_MULT*` helpers, `struct ccu_mult`, `SUNXI_CCU_N_WITH_GATE_LOCK`, and `ccu_mult_ops`.

## Control Flow
There is no runtime flow. Static descriptors built here are handled by `ccu_mult.c`.

## State And Persistence
State fields include enable mask, lock bit, optional fractional descriptor, multiplier bitfield, optional mux, and common register metadata.

## Dependencies And Integration Points
It depends on `ccu_common`, `ccu_frac`, and `ccu_mux`. It integrates with SoC PLL descriptors, notably A80 CPU PLLs.

## Risks
Offset/min/max fields encode hardware-specific multiplier semantics. Incorrect min values can program out-of-range CPU PLL frequencies.

## Test Signals
Compile and PLL rate-change tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.c

## Purpose
`ccu_mux.c` implements parent selection helpers and standalone mux clock ops for sunxi-ng clocks, including fixed/variable predivider support and safe reparenting notifiers.

## Important APIs, Types, And Functions
Important APIs are `ccu_mux_helper_apply_prediv()`, `ccu_mux_helper_determine_rate()`, `ccu_mux_helper_get_parent()`, `ccu_mux_helper_set_parent()`, exported `ccu_mux_ops`, and `ccu_mux_notifier_register()`.

## Control Flow
Rate determination iterates parents unless `CLK_SET_RATE_NO_REPARENT` is set, applies predividers, delegates class-specific rounding, unapplies predividers for parent-rate requests, and chooses the best rate. Parent changes apply optional sparse tables, key-field unlock values, and update bits under the CCU lock. Notifiers temporarily switch to a bypass parent before PLL rate changes and restore after.

## State And Persistence
State is hardware mux fields plus `ccu_mux_nb.original_index` during notifier callbacks. No persistent storage exists.

## Dependencies And Integration Points
Dependencies include CCF, delay, MMIO, gates, common feature flags, and consumers from every compound clock class.

## Risks
Risks include incorrect sparse mux tables, predivider handling, key-field writes, and notifier delay/bypass configuration. A bad parent switch can destabilize CPU or bus clocks during PLL changes.

## Test Signals
Test with clock parent changes, rate requests across parent choices, CPU/PLL notifier paths, and clock-summary parent/rate verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.h

## Purpose
This header declares mux descriptors, predivider descriptors, constructor macros, helper prototypes, and notifier state for sunxi-ng mux clocks.

## Important APIs, Types, And Functions
Important types are `ccu_mux_fixed_prediv`, `ccu_mux_var_prediv`, `ccu_mux_internal`, `ccu_mux`, and `ccu_mux_nb`; macros include `_SUNXI_CCU_MUX*`, `SUNXI_CCU_MUX*`, and parent-data/hardware variants.

## Control Flow
No runtime flow is present. It defines data consumed by `ccu_mux.c` and by compound classes embedding `ccu_mux_internal`.

## State And Persistence
State includes bit offsets/widths, optional selector table, fixed/variable predivider arrays, enable bit, and notifier original-parent storage.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration reaches CPU muxes, bus roots, module clocks, display clocks, and notifier-safe PLL consumers.

## Risks
Selector tables and predivider arrays must match hardware selector values, not logical parent indexes. Wrong values are hard to diagnose because clocks still register.

## Test Signals
Compile, parent selection, and rate determination tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.c

## Purpose
`ccu_nk.c` implements the sunxi-ng common-clock-framework operations for N*K multiplier PLL clocks with optional fixed postdivision clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. The search chooses the highest representable rate not above the request and waits for a PLL lock bit after programming.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.h

## Purpose
This header declares the N*K PLL clock class.

## Important APIs, Types, And Functions
It defines `struct ccu_nk`, `SUNXI_CCU_NK_WITH_GATE_LOCK_POSTDIV`, `hw_to_ccu_nk()`, and `ccu_nk_ops`.

## Control Flow
There is no runtime flow; the macro creates static descriptors for `ccu_nk.c`.

## State And Persistence
Descriptor state includes enable and lock bits, N/K multiplier fields, fixed postdivider, and common metadata.

## Dependencies And Integration Points
Dependencies are CCF, common/div/mult headers. Integration is with peripheral PLL descriptors in SoC CCU files.

## Risks
Postdivider and offset fields are easy to misencode, which changes every child clock rate.

## Test Signals
PLL rate-change tests and lock-wait behavior validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.c

## Purpose
`ccu_nkm.c` implements the sunxi-ng common-clock-framework operations for N*K/M PLL clocks with optional parent-rate adjustment and hardware validity constraints clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It enforces optional maximum M/N ratio and minimum parent/M ratio constraints when selecting factors.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.h

## Purpose
This header declares the N*K/M clock class used for PLLs that multiply by N and K then divide by M.

## Important APIs, Types, And Functions
Important items are `struct ccu_nkm`, `SUNXI_CCU_NKM_WITH_MUX_GATE_LOCK`, `SUNXI_CCU_NKM_WITH_GATE_LOCK`, factor fields, optional fixed postdivider, and ratio constraints.

## Control Flow
No runtime flow lives here. It provides descriptors for `ccu_nkm.c`.

## State And Persistence
State is descriptor-only until probe initializes `ccu_common`; hardware factor fields are then read/written by ops.

## Dependencies And Integration Points
It depends on CCF and common/div/mult headers. SoC PLL descriptors use it for DDR and similar clocks.

## Risks
Ignoring `max_m_n_ratio` or `min_parent_m_ratio` can let rate selection choose unstable hardware combinations.

## Test Signals
Build plus PLL rate tests with constrained descriptors validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.c

## Purpose
`ccu_nkmp.c` implements the sunxi-ng common-clock-framework operations for N*K/M/P PLL clocks using 64-bit intermediate arithmetic clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It clamps optional maximum rates and explicitly handles zero-width fields to avoid invalid `GENMASK()` usage.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.h

## Purpose
This header declares the N*K/M/P PLL class used by CPU and peripheral PLL descriptors.

## Important APIs, Types, And Functions
It defines `struct ccu_nkmp`, `SUNXI_CCU_NKMP_WITH_GATE_LOCK`, conversion helper, and `ccu_nkmp_ops`.

## Control Flow
There is no runtime control flow. Static descriptors are interpreted by `ccu_nkmp.c`.

## State And Persistence
Descriptor state includes enable/lock bits, N/K multiplier fields, M/P divider fields, optional fixed postdivider, optional max rate, and common metadata.

## Dependencies And Integration Points
It depends on CCF and common/div/mult headers. Integration is with PLL-heavy SoC CCU files such as V3s and A80.

## Risks
The P field is power-of-two encoded in the implementation. Width-zero fields are legal for some hardware and must be handled carefully.

## Test Signals
PLL programming tests, CPU clock changes, and clock-summary rate checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.c

## Purpose
`ccu_nm.c` implements the sunxi-ng common-clock-framework operations for N/M PLL clocks with optional fractional and sigma-delta modulation modes clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It checks min/max rates, exact fractional/SDM rates, programs SDM-required factors when needed, and waits for lock after writes.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.h

## Purpose
This header declares the N/M PLL class and the macros for fractional, SDM, min/max, closest-rate, and simple gated variants.

## Important APIs, Types, And Functions
Important items are `struct ccu_nm`, `SUNXI_CCU_NM_WITH_SDM_GATE_LOCK`, `SUNXI_CCU_NM_WITH_FRAC_GATE_LOCK*`, `SUNXI_CCU_NM_WITH_GATE_LOCK`, and `ccu_nm_ops`.

## Control Flow
No runtime flow exists in the header. Macros create descriptors consumed by `ccu_nm.c`.

## State And Persistence
State includes enable/lock bits, N/M fields, fractional and SDM descriptors, fixed postdivider, min/max rates, and common metadata.

## Dependencies And Integration Points
It depends on common/div/frac/mult/sdm headers. It integrates with audio, video, VE, ISP, and other PLL descriptors.

## Risks
Fractional and SDM modes have exact-rate semantics. Incorrect min/max or feature bits can bypass the intended path and program unstable integer factors.

## Test Signals
Test with audio SDM rates, video fractional rates, normal integer PLL rates, and lock-wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.c

## Purpose
`ccu_phase.c` implements phase-only clock ops used for MMC sample/output clock delay controls.

## Important APIs, Types, And Functions
Important callbacks are `ccu_phase_get_phase()` and `ccu_phase_set_phase()` exported through `ccu_phase_ops`.

## Control Flow
Get/set derive phase steps from parent and grandparent clock rates, treating register delay value zero as 180 degrees. Set computes the nearest delay value, updates the phase bitfield under the shared lock, and returns through CCF phase APIs.

## State And Persistence
The only state is the delay bitfield in the module clock register. There is no persistent software state.

## Dependencies And Integration Points
It depends on CCF parent traversal, MMIO, spinlocks, and `ccu_common`. It integrates mainly with MMC host drivers using sample/output phase clocks.

## Risks
Rate assumptions matter: if parent or grandparent rates are unavailable or not an integer divider relationship, phase calculation can fail or be inaccurate. The zero-means-180 hardware convention must be preserved.

## Test Signals
Test with MMC tuning, `clk_get_phase()`/`clk_set_phase()` calls, and card I/O at multiple bus speeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.h

## Purpose
This header declares the phase clock descriptor used by sunxi-ng MMC sample/output clocks.

## Important APIs, Types, And Functions
It defines `struct ccu_phase`, `SUNXI_CCU_PHASE`, `hw_to_ccu_phase()`, and `ccu_phase_ops`.

## Control Flow
There is no runtime flow; the macro builds descriptors operated on by `ccu_phase.c`.

## State And Persistence
Descriptor state is shift, width, register offset, and embedded `clk_hw` metadata.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration is with SoC CCU files that expose MMC phase clocks.

## Risks
Wrong shift/width values can corrupt the main MMC divider or mux fields sharing the same register.

## Test Signals
MMC phase set/get and data-transfer tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.c

## Purpose
`ccu_reset.c` implements reset-controller operations for reset bits embedded in sunxi-ng CCU registers.

## Important APIs, Types, And Functions
Important callbacks are `ccu_reset_assert()`, `ccu_reset_deassert()`, `ccu_reset_reset()`, `ccu_reset_status()`, and exported `ccu_reset_ops`.

## Control Flow
Assert clears the hardware bit, deassert sets it, reset pulses assert then delays 10 microseconds before deassert, and status inverts hardware convention so reset-controller semantics return true when reset is asserted.

## State And Persistence
State is hardware reset bits protected by the CCU spinlock. No software persistence exists.

## Dependencies And Integration Points
It depends on reset-controller core, MMIO, delay, spinlocks, and reset maps supplied by each provider.

## Risks
The hardware uses active-low reset bits, opposite the reset API expectation. Wrong inversion would make every consumer see or drive reset backwards.

## Test Signals
Test by probing reset consumers, using debug reset controls where available, and verifying peripherals recover after reset pulses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.h

## Purpose
This header declares the reset map and provider state used by sunxi-ng CCU reset controllers.

## Important APIs, Types, And Functions
It defines `struct ccu_reset_map`, `struct ccu_reset`, `rcdev_to_ccu_reset()`, and `ccu_reset_ops`.

## Control Flow
No runtime flow exists here; provider code fills the map and `ccu_common.c` registers the controller.

## State And Persistence
State fields include MMIO base, reset map pointer, shared lock, and embedded `reset_controller_dev`.

## Dependencies And Integration Points
It depends on reset-controller and spinlock headers. Integration is through every sunxi-ng SoC descriptor exposing resets.

## Risks
The map is indexed by public reset IDs, so missing or reordered entries break DT reset specifiers.

## Test Signals
Build and reset-controller probe/use tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.c

## Purpose
`ccu_sdm.c` supports sigma-delta modulation helper paths for exact audio PLL rates where the hardware pattern is table-driven rather than algorithmically derived.

## Important APIs, Types, And Functions
Important APIs are `ccu_sdm_helper_is_enabled()`, `enable()`, `disable()`, `has_rate()`, `read_rate()`, and `get_factors()`, exported in the `SUNXI_CCU` namespace.

## Control Flow
Enable writes the matching pattern to the tuning register, sets the tuning enable bit, then sets the PLL SDM enable bit if present. Disable clears both enables. Rate reads match current pattern plus M/N factors against the table because generic effective-rate calculation is not known.

## State And Persistence
State is hardware SDM enable bits and tuning pattern registers. The supported rate table is static descriptor data.

## Dependencies And Integration Points
It depends on CCF debug names, MMIO, spinlocks, and `ccu_common`. It integrates with `ccu_nm` audio PLL descriptors.

## Risks
The code intentionally supports only table-known rates, mainly 22.5792 MHz and 24.576 MHz audio-family rates. Unknown patterns read as 0, so changing vendor pattern values needs hardware validation.

## Test Signals
Test with audio playback/capture at 44.1 kHz and 48 kHz families, clk-summary rate readback, and transitions between SDM and non-SDM rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.h

## Purpose
This header defines sigma-delta modulation table entries and descriptor state for sunxi-ng PLLs.

## Important APIs, Types, And Functions
Important types are `struct ccu_sdm_setting` and `struct ccu_sdm_internal`; `_SUNXI_CCU_SDM()` fills the descriptor and helper prototypes declare the runtime API.

## Control Flow
There is no runtime flow in the header. It stores static table data consumed by `ccu_sdm.c`.

## State And Persistence
Descriptor state includes supported rates, raw vendor pattern words, M/N factors, optional PLL enable bit, tuning enable bit, and tuning register offset.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`; integration is through `ccu_nm` descriptors using `CCU_FEATURE_SIGMA_DELTA_MOD`.

## Risks
The comments document unknown hardware pattern semantics. Treat pattern words as hardware-calibrated constants, not values to recompute casually.

## Test Signals
Audio exact-rate tests validate descriptor entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/Kconfig

## Purpose
This Kconfig file controls build selection for the legacy Allwinner `drivers/clk/sunxi` clock providers.

## Important APIs, Types, And Functions
It defines `CLK_SUNXI`, `CLK_SUNXI_CLOCKS`, and PRCM options for SUN6I, SUN8I, and SUN9I. `CLK_SUNXI_CLOCKS` depends on `ARCH_SUNXI || COMPILE_TEST` and defaults for legacy ARM multi-v7 sunxi builds.

## Control Flow
Kconfig has no runtime flow. Menu selections determine which objects in the Makefile are compiled into the kernel.

## State And Persistence
No runtime state exists. Build configuration is the persistent artifact in `.config`.

## Dependencies And Integration Points
It depends on the kernel Kconfig system, architecture symbols, `MFD_SUN6I_PRCM`, and common clock support. It integrates with DT-driven early clock initialization and PRCM platform support.

## Risks
Wrong dependencies can either omit required early clocks or build providers on unsupported platforms. Default changes can affect legacy boards.

## Test Signals
Test by building sunxi defconfigs, COMPILE_TEST configurations, and PRCM-enabled configs, then booting legacy A10/A20/A31/A80-style DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/Makefile

## Purpose
This Makefile maps legacy sunxi clock Kconfig symbols to object files.

## Important APIs, Types, And Functions
It always builds `clk-factors.o` for `CONFIG_CLK_SUNXI`; builds many legacy providers under `CONFIG_CLK_SUNXI_CLOCKS`; and builds PRCM-specific APB/AR100/CPUS providers for SUN6I/SUN8I/SUN9I options.

## Control Flow
There is no runtime flow. Kbuild evaluates object lists during compilation.

## State And Persistence
No runtime state exists. The build graph is determined by `.config`.

## Dependencies And Integration Points
It depends on Kbuild and the source files in this directory. Integration is with early `CLK_OF_DECLARE` providers and platform drivers.

## Risks
Omitting an object can make DT compatible strings unresolved at boot. Adding an object under the wrong config can introduce unused code or link failures.

## Test Signals
Build tests across all sunxi Kconfig combinations and boot logs for clock-provider registration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-codec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-codec.c

## Purpose
This legacy provider registers the simple A10 codec gate clock from a device-tree clock node.

## Important APIs, Types, And Functions
The key function is `sun4i_codec_clk_setup()`, declared with `CLK_OF_DECLARE` for `allwinner,sun4i-a10-codec-clk`. It maps one register and registers a gate at bit 31 with `CLK_SET_RATE_PARENT`.

## Control Flow
At early OF clock init, the setup maps MMIO, reads `clock-output-names`, gets the first parent name, registers the gate, and adds a simple OF clock provider if registration succeeds.

## State And Persistence
State is only the hardware gate bit and the registered CCF clock. There is no cleanup path for this early provider.

## Dependencies And Integration Points
It depends on CCF, OF, and OF address mapping. It integrates with legacy audio codec consumers using this DT compatible.

## Risks
Lack of error logging can hide mapping failures. The gate bit and parent-rate propagation must match codec clock hardware.

## Test Signals
Test by booting A10 DTs with codec audio, confirming clock provider registration, and validating audio playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-hosc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-hosc.c

## Purpose
This legacy provider registers the gated 24 MHz high-speed oscillator as a composite fixed-rate plus gate clock.

## Important APIs, Types, And Functions
The setup function `sun4i_osc_clk_setup()` handles `allwinner,sun4i-a10-osc-clk`. It allocates `clk_fixed_rate` and `clk_gate`, reads `clock-frequency`, maps the gate register, and registers a composite clock.

## Control Flow
Early OF init reads the frequency, allocates components, fills gate bit 0 and fixed-rate data, registers the composite, and adds a simple provider.

## State And Persistence
State is the oscillator gate bit and registered CCF objects. The frequency comes from DT; there is no runtime recalculation beyond fixed-rate ops.

## Dependencies And Integration Points
It depends on CCF, OF properties, OF mapping, and dynamic allocation. It is a root parent for many legacy sunxi clocks.

## Risks
Failure to map the register after allocation can leak resources, consistent with early boot provider style. Wrong frequency in DT propagates to every child clock.

## Test Signals
Test by checking root oscillator rate in clk-summary and successful boot of downstream legacy clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-hosc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-mod1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-mod1.c

## Purpose
This legacy provider registers MOD1-style module clocks as mux plus gate composites.

## Important APIs, Types, And Functions
`sun4i_mod1_clk_setup()` handles `allwinner,sun4i-a10-mod1-clk`, using mux bits 16..17, gate bit 31, up to four parents, and `CLK_SET_RATE_PARENT`.

## Control Flow
At early init it maps the register, allocates mux and gate structures, fills parents and output name, registers a composite mux/gate clock, and adds a simple OF provider.

## State And Persistence
State is the mux selector and gate bit in the hardware register. No software persistence exists.

## Dependencies And Integration Points
It depends on CCF composite helpers, OF mapping, and the shared spinlock. It integrates with legacy module clocks that use MOD1 layout.

## Risks
Resource cleanup is limited to error paths. Parent count and mux width must match DT/hardware or parent selection will be wrong.

## Test Signals
Test with legacy devices using MOD1 clocks and parent switching/rate propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-mod1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-pll2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-pll2.c

## Purpose
This legacy provider registers the A10/A13 PLL2 audio clock and its four fixed-factor outputs.

## Important APIs, Types, And Functions
Important logic is `sun4i_pll2_setup()`, wrappers for A10 and A13 compatibles, divider/multiplier/gate composite setup for `pll2-base`, and fixed-factor outputs indexed by `dt-bindings/clock/sun4i-a10-pll2.h`.

## Control Flow
Early init maps MMIO, allocates a onecell provider, registers a predivider, gate, multiplier composite, forces the post divider register field to 4 with an SoC-specific offset, registers 1x/2x/4x/8x outputs, and adds the onecell provider.

## State And Persistence
State is PLL2 register fields and registered CCF clocks. Probe writes the postdivider value during initialization.

## Dependencies And Integration Points
It depends on CCF divider/multiplier/gate/fixed-factor helpers, OF mapping, allocations, and PLL2 binding IDs. It integrates with legacy audio clock consumers.

## Risks
PLL2 is audio-critical; postdivider offset differs between A10 and A13. Partial registration failures can leave earlier clocks registered. Incorrect fixed factors break audio sample-rate families.

## Test Signals
Test by booting A10/A13 DTs, inspecting PLL2 output rates, and validating audio playback at 44.1/48 kHz families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-pll2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-ve.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-ve.c

## Purpose
This legacy provider registers the A10 video-engine clock and a reset controller backed by the same register.

## Important APIs, Types, And Functions
Important items are `ve_reset_data`, reset ops `sunxi_ve_reset_assert()` and `deassert()`, `sunxi_ve_of_xlate()`, and `sun4i_ve_clk_setup()` for `allwinner,sun4i-a10-ve-clk`.

## Control Flow
Early init maps the register, allocates divider and gate components, registers a composite clock with divider bits 16..18 and gate bit 31, adds an OF clock provider, then allocates/registers a one-reset reset controller using bit 0.

## State And Persistence
State is the VE divider, gate, and reset bit. Reset bit semantics are active-high deassert like sunxi CCU conventions.

## Dependencies And Integration Points
It depends on CCF, reset-controller core, OF mapping, and spinlocks. It integrates with video-engine drivers needing both a functional clock and reset.

## Risks
Clock and reset share one register, so locking is required. Error paths must avoid leaving providers without reset data. Reset xlate requires zero cells.

## Test Signals
Test by probing VE hardware, toggling reset, setting VE rate, and verifying video decode/encode paths where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-ve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a20-gmac.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a20-gmac.c

## Purpose
This legacy provider models the A20/A31 GMAC clock module as a two-parent mux plus gate composite for MAC/PHY transmit clock selection.

## Important APIs, Types, And Functions
Important data includes `sun7i_a20_gmac_mux_table`, gate bit `SUN7I_A20_GMAC_GPIT`, mux mask `SUN7I_A20_GMAC_MASK`, and `sun7i_a20_gmac_clk_setup()` declared for `allwinner,sun7i-a20-gmac-clk`.

## Control Flow
Early init reads the output name, allocates mux/gate, requires exactly two parents, maps the register, registers a composite, and adds a simple provider.

## State And Persistence
State is the mux selector and PHY output gate bit. The GMAC driver is expected to select parent/rate according to MII/GMII/RGMII mode.

## Dependencies And Integration Points
It depends on CCF composite helpers, OF parent data, and GMAC DT wiring. It integrates directly with the sunxi GMAC Ethernet driver and external PHY clocking.

## Risks
Selecting the wrong parent can allow RX but prevent TX traffic. The optional external 125 MHz path is intentionally not fully modeled for simplicity.

## Test Signals
Test with Ethernet link-up and traffic in MII/GMII/RGMII modes, parent selection changes from the GMAC driver, and clk-summary parent/gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a20-gmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.c

## Purpose
`clk-factors.c` is the legacy adjustable factor-based clock implementation used before sunxi-ng. It registers composite clocks with optional mux and gate around a custom factor-rate component.

## Important APIs, Types, And Functions
Important functions are `clk_factors_recalc_rate()`, `clk_factors_determine_rate()`, `clk_factors_set_rate()`, `__sunxi_factors_register()`, public `sunxi_factors_register()`, `sunxi_factors_register_critical()`, and `sunxi_factors_unregister()`.

## Control Flow
Rate recalculation decodes N/K/M/P fields and either calls a custom recalc hook or applies `(parent * (n + n_start) * (k + 1) >> p) / (m + 1)`. Rate determination tries all parents and calls the SoC getter. Set-rate computes factors, updates fields under an optional lock, writes the register, and delays for PLL stabilization. Registration builds a composite with optional mux/gate and an OF provider.

## State And Persistence
State includes allocated `clk_factors`, optional mux/gate structures, and hardware factor fields. No disk persistence exists; unregister frees allocated pieces but notes composite internals may leak.

## Dependencies And Integration Points
It depends on CCF, OF, MMIO, allocation helpers, and legacy factor-data callbacks. It integrates with `clk-mod0.c` and other legacy sunxi clock providers.

## Risks
The generic formula depends on callback-specific raw field conventions. The register mask macros assume nonzero widths. The register function currently passes `CLK_IS_CRITICAL` to composites regardless of the `flags` argument, which is a behavioral detail to preserve or fix deliberately.

## Test Signals
Test with legacy MOD0/MMC/MBUS clocks, PLL factor clocks, parent-rate propagation, and clk-summary recalculated rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.h

## Purpose
This header defines the data contract for legacy sunxi factor clocks.

## Important APIs, Types, And Functions
Important types are `clk_factors_config`, `factors_request`, `factors_data`, and `clk_factors`, plus registration and unregister prototypes.

## Control Flow
There is no runtime flow in the header. Provider files fill `factors_data` callbacks and bitfield tables that `clk-factors.c` consumes.

## State And Persistence
State fields describe bit shifts/widths, requested and computed factors, optional mux/gate settings, callbacks, register pointer, and cleanup pointers.

## Dependencies And Integration Points
It depends on CCF and spinlocks. Integration is with legacy providers such as `clk-mod0.c` and old PLL/module clock code.

## Risks
The sentinel `SUNXI_FACTORS_NOT_APPLICABLE` is zero, so width zero means absent. Callback authors must return raw register field values, not always arithmetic factors.

## Test Signals
Build plus rate tests for each legacy factor user validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-mod0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-mod0.c

## Purpose
This legacy provider implements MOD0-style module clocks, A13 MBUS, A10/A80 MMC clocks, and MMC sample/output phase subclocks.

## Important APIs, Types, And Functions
Important functions/data include `sun4i_a10_get_mod0_factors()`, `sun4i_a10_mod0_data`, early and platform-driver registration for `allwinner,sun4i-a10-mod0-clk`, A80 MOD0 data, A13 MBUS critical setup, `struct mmc_phase`, `mmc_get_phase()`, `mmc_set_phase()`, `sunxi_mmc_setup()`, and A10/A80 MMC OF declarations.

## Control Flow
MOD0 setup maps registers and calls `sunxi_factors_register()`. The platform driver covers cases where MFD resources are not available during early `CLK_OF_DECLARE`. MMC setup registers the main factors clock plus two phase clocks in a onecell provider.

## State And Persistence
State is factor register fields, gate/mux bits, and phase delay fields. MBUS is registered critical to avoid accidental disable.

## Dependencies And Integration Points
It depends on legacy `clk-factors`, CCF, OF/platform mapping, and spinlocks. It integrates with storage, module peripherals, MBUS, and MMC host drivers.

## Risks
MOD0 clocks only divide, so requests above the parent are clamped. MMC phase calculations assume parent/grandparent rates form a clean divider. The dual early/platform registration path prevents missing clocks but must avoid duplicate registration on the same node.

## Test Signals
Test MOD0 peripheral rates, A13 MBUS stability, A10/A80 MMC card I/O, phase set/get, and MFD-instantiated mod0 probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-mod0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-simple-gates.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-simple-gates.c

## Purpose
This legacy provider registers arrays of simple gate clocks from DT `clock-indices`/`clock-output-names` properties.

## Important APIs, Types, And Functions
Important functions are `sunxi_simple_gates_setup()`, `sunxi_simple_gates_init()`, protected variants for A10/A10s/A13/A20 AHB and A10 DRAM gates, and many `CLK_OF_DECLARE` compatible bindings.

## Control Flow
Early init maps the gate register block, reads the parent, allocates a onecell array sized by the largest index, registers one `clk_register_gate()` per listed index, optionally enables protected critical gates, and adds an OF provider.

## State And Persistence
State is gate bits in one or more 32-bit registers and the registered onecell provider. Protected gates are enabled during setup and left on.

## Dependencies And Integration Points
It depends on CCF, OF property parsing, OF address mapping, and shared spinlock. It integrates with many legacy bus-gate DT nodes across sun4i/sun5i/sun6i/sun7i/sun8i/sun9i.

## Risks
The code trusts DT property consistency. A bad largest index can undersize the array; wrong protected indices can disable SDRAM/DRAM outputs. Error cleanup releases the mapped resource only on early allocation failure.

## Test Signals
Test with legacy board boot, clock lookups for all gate IDs, protected SDRAM/DRAM clocks staying enabled, and peripheral gate enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-simple-gates.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-display.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-display.c

## Purpose
This legacy provider registers sun4i display/TCON channel clocks as mux-divider-gate composites and exposes reset controls backed by the same display clock register.

## Important APIs, Types, And Functions
Important structures are `sun4i_a10_display_clk_data` for divider/mux/gate/reset bit layout and flags, `reset_data`, reset ops, `sun4i_a10_display_reset_xlate()`, common initializer `sun4i_a10_display_init()`, and setup wrappers for `allwinner,sun4i-a10-tcon-ch0-clk` and `allwinner,sun4i-a10-display-clk`.

## Control Flow
Early setup maps the register, creates divider/mux/gate components based on per-compatible layout data, registers a composite display clock, adds an OF clock provider, and, when reset bits are defined, registers a reset controller with one or more resets.

## State And Persistence
State is the display clock mux/divider/gate fields and reset bits in hardware. No software persistence exists beyond allocated CCF/reset objects.

## Dependencies And Integration Points
It depends on CCF composite helpers, OF mapping, reset-controller core, and a shared spinlock. It integrates with sun4i display/TCON/DRM consumers and display reset users.

## Risks
Clock and reset fields share one register; missing locking can corrupt adjacent bits. Different compatibles use different divider widths and reset layouts, so descriptor data must match hardware. Reset xlate validates reset specifier cells.

## Test Signals
Test by booting display-capable sun4i DTs, validating TCON/display clock rates and parents, display output, and reset-controller operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-pll3.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-pll3.c

## Purpose
This legacy provider registers the sun4i A10 PLL3 video clock as a gate plus divider composite.

## Important APIs, Types, And Functions
The key function is `sun4i_a10_pll3_setup()` declared for `allwinner,sun4i-a10-pll3-clk`. It uses gate bit 31 and a 7-bit divider at shift 0.

## Control Flow
Early init maps the PLL register, creates divider and gate components, reads the output name and parent, registers a composite clock with `CLK_SET_RATE_PARENT`, and adds a simple OF provider.

## State And Persistence
State is the PLL3 gate and divider fields. There is no cleanup/persistence outside the registered clock.

## Dependencies And Integration Points
It depends on CCF composite helpers, OF mapping, and a spinlock. It integrates with legacy display/video clock consumers that need PLL3-derived rates.

## Risks
Video PLL rates are display-sensitive; wrong divider width or parent propagation can break pixel clocks. Early provider allocation failure paths must avoid using unmapped registers.

## Test Signals
Test by checking PLL3 rates in clk-summary and validating display modes that depend on PLL3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-pll3.c -->
