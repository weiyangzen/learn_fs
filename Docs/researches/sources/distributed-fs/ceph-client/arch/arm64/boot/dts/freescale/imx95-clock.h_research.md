## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-clock.h

### Purpose
This file defines the devicetree clock IDs for NXP i.MX95. It is the symbolic binding layer between DTS `clocks` properties and the i.MX95 clock provider, with the opening source IDs explicitly matching i.MX95 SCMI firmware indices.

### Important APIs, Types, And Functions
There are no C functions or structs. The public API is the `IMX95_CLK_*` macro set. IDs 1-40 cover fixed or firmware-visible clock sources such as 32 kHz, 24 MHz, FRO, system/audio/video/ARM/DRAM/HSIO/LDB PLLs, and external inputs. `IMX95_CCM_NUM_CLK_SRC` is set to 41 and roots are then expressed as offsets from it, covering peripheral roots, bus roots, GPU/NPU/VPU/camera/display/HSIO/NETC clocks, wakeup clocks, selector clocks, and a GPU CGC gate.

### Control Flow
The header has no executable control flow. During DTS compilation, these macros become integer clock specifiers. At runtime, platform clock drivers decode those IDs from the device tree and route operations through the common clock framework or SCMI clock provider.

### State, Persistence, And Dependencies
The header carries no runtime state. Its persistent effect is in compiled DTBs. It depends on the i.MX95 SCMI firmware clock index contract for the first block and on the Linux i.MX95 CCM driver understanding the root and gate IDs after `IMX95_CCM_NUM_CLK_SRC`.

### Integration Points
Integration points include `imx95.dtsi`, board-level DTS files, the i.MX95 CCM/SCMI clock provider, common clock framework consumers, and peripheral nodes for UART, I2C, SPI, CAN, USDHC, audio, display, GPU, NPU, VPU, camera, HSIO, and NETC.

### Risks
Changing existing values is an ABI break for DTBs. The offset scheme around `IMX95_CCM_NUM_CLK_SRC` makes insertion errors easy: adding a source or root in the wrong position can shift many downstream IDs. Reserved source IDs 20-23 are deliberate holes and should not be casually repurposed without matching firmware and driver support.

### Test Signals
Useful signals include ARM64 `dtbs_check`, boot-time clock provider probe success, `/sys/kernel/debug/clk/clk_summary` entries for i.MX95 roots, and functional tests for clock-sensitive peripherals such as USDHC, LPUART, NETC, GPU/NPU/VPU, and display. Source reading signal: 188 lines; 176 `#define` entries; no includes or functions.
