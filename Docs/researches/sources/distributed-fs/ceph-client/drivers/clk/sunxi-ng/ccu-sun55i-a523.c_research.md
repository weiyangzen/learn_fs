# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523.c

Purpose: main CCU driver for Allwinner A523. It describes a large modern Sunxi clock tree including PLL output families, CPU/AXI/bus roots, DMA/MBUS, storage, network, USB, display, video, camera, audio, sensor, and reset domains.

Important APIs, types, and functions: uses parent-data based CCU definitions and fixed factors for PLL-periph, video, audio, and other derived outputs. Central artifacts are `sun55i_a523_ccu_clks`, `sun55i_a523_hw_clks`, `sun55i_a523_ccu_resets`, `sun55i_a523_ccu_desc`, `pll_regs`, and `sun55i_a523_ccu_probe()`. It also includes `<dt-bindings/clock/sun55i-a523-ccu.h>` and reset bindings directly.

Control flow: probe maps the CCU resource, iterates over all modeled PLL registers to set PLL enable, LDO enable, and lock-enable bits that are not represented independently by generic PLL structs, forces PLL_AUDIO0 `m1/m0` output-divider defaults, and registers the descriptor with `devm_sunxi_ccu_probe()`.

State and persistence: all persistent state is MMIO clock/reset state. Software descriptors are static. Some clocks are marked critical, including DDR, to prevent framework disablement of essential infrastructure.

Dependencies and integration points: binds `allwinner,sun55i-a523-ccu`, provides parent PLLs used by R/MCU CCUs, and clocks/resets for CPU, memory, DMA, VE, NPU, GPU, display, HDMI, MIPI DSI, TCON, LVDS/eDP, CSI/ISP, USB, PCIe/USB3, EMAC, SPI, I2C, UART, CAN, thermal, GPADC, LRADC, LEDC, and audio blocks.

Risks and test signals: this is mostly data-table code, so risks are wrong parent order, register offsets, reset bits, fixed-factor modeling, and PLL enable semantics. Comments flag BSP/register-derived resets. Test signals include full boot without missing parent warnings, clk summary review for PLL families, peripheral probe coverage across storage/network/display/camera/audio/USB, reset-controller exercise, and power-management tests verifying critical clocks stay enabled.
