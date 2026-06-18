# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp.c

## Purpose
This platform driver registers the main i.MX8M Plus CCM clock provider. It defines the full PLL, bus, peripheral, media, HDMI, GPU/NPU/VPU, audio, storage, network, USB, and CPU clock tree and applies datasheet-derived maximum rate constraints based on common and operating-mode-specific limits.

## Important APIs, Types, And Functions
`imx8mp_clocks_probe()` is the main entry point for `fsl,imx8mp-ccm`. It maps anatop and CCM resources, allocates a onecell provider, registers PLL14xx clocks, bypass muxes, fixed-factor outputs, i.MX8M composites, gates, shared gates, DRAM firmware-managed clocks, and the CPU clock. `struct imx8mp_clock_constraints` plus `imx8mp_clock_common_constraints`, `imx8mp_clock_nominal_constraints`, and `imx8mp_clock_overdrive_constraints` define maximum rates; `imx8mp_clocks_apply_constraints()` applies them with `clk_hw_set_rate_range()`. The driver publishes clocks with `of_clk_add_hw_provider()` and suppresses unbind through the platform driver.

## Control Flow
Probe maps `fsl,imx8mp-anatop` and the CCM resource, creates dummy/external clocks, registers audio/video/DRAM/GPU/VPU/ARM/SYS_PLL1/2/3 PLLs, bypass selectors, output gates, SYS PLL fixed-factor rates, and CLKOUT clocks. It then creates A53, M7, ML, GPU, audio, HSIO, media, bus, NOC, AHB, MIPI, DRAM, VPU, CAN, PCIe, I2C, SAI, ENET, NAND/QSPI/USDHC, UART, USB, GIC, ECSPI, PWM, GPT, watchdog, HDMI, camera, display, LDB, memrepair, PDM, and SAI7 composites and gates. Shared gate counters cover NAND, USB, media, and audio root groups. After validation, it applies common constraints, optionally applies `fsl,operating-mode = "nominal"` or `"overdrive"` constraints, registers the provider, and registers UART clocks.

## State And Persistence
Hardware state persists in anatop and CCM registers. Global `clk_hw_data` and `hws` are retained for the module lifetime. No suspend save/restore is implemented here; the clock framework and hardware retain state, while DRAM alt/APB roots are firmware-managed because TF-A can change DRAM clocks. Rate-range constraints persist in the common clock framework once applied. Critical clocks protect DRAM, NOC, AHB, GIC, memrepair, and related roots from disable/rate misuse.

## Dependencies And Integration Points
Dependencies include `dt-bindings/clock/imx8mp-clock.h`, `linux/units.h` for `HZ_PER_MHZ`, `fsl,imx8mp-anatop`, `fsl,imx8mp-ccm`, external input names, PLL14xx data, i.MX8M composite helpers, and the common clock framework. Consumers include CPUfreq, GPU/NPU/VPU/media/HDMI/display, audio/audiomix, ENET/ENET_QOS, PCIe, USB, USDHC, QSPI/NAND, CAN, I2C, UART, PWM, GPT, watchdog, and thermal/sensor blocks. The audio block driver depends on many parent clocks exported here.

## Risks And Test Signals
Risks are higher than the other table drivers because rate constraints affect runtime `clk_set_rate()` behavior. Wrong limits can cap performance or permit unsafe overclocking. Other risks include mismatched operating-mode property handling, missing critical flags, shared gate counters disabling grouped media/audio/USB clocks too early, firmware-managed DRAM conflicts, and parent-name mismatches with the audiomix driver. Test signals include clean boot with no missing clock IDs, correct provider registration, clk-summary coverage, CPUfreq and OPP operation in nominal/overdrive modes, `clk_hw_set_rate_range()` limiting affected clocks, stable DRAM under TF-A management, and functional HDMI/media/camera/GPU/NPU/VPU/audio/USB/PCIe/ENET/USDHC/QSPI/NAND/CAN/serial peripherals.
