# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-kirkwood.c

Purpose: this file is the Kirkwood/Discovery Innovation table driver for MV88F6180, 6190, 6192, 6281, 6282, 98DX4122, and 98DX1135 pinmuxing. It exposes a shared MPP table with variant masks and per-SoC pin counts/GPIO ranges.

Important APIs, types, and functions: the `V()` macro encodes seven variant bits. `mv88f6xxx_mpp_modes[]` lists MPP0-49 with functions including GPIO/GPO, NAND, SPI, UART, SATA, LCD, PTP, TWSI, SDIO, audio, TS, TDM, GE/MII, and switch-specific NAND signals. `mv88f6180_info`, `mv88f6190_info`, `mv88f6192_info`, `mv88f6281_info`, `mv88f6282_info`, `mv98dx4122_info`, and `mv98dx1135_info` bind variants to control ranges and GPIO ranges. `kirkwood_pinctrl_probe()` delegates to `mvebu_pinctrl_simple_mmio_probe()`.

Control flow: OF match returns the prebuilt SoC info. Probe stores it as platform data, maps one MMIO MPP resource through the shared helper, and the MVEBU core filters settings by variant while building functions. Pinmux requests are simple 4-bit MMIO updates.

State and persistence behavior: all SoC data is static. Device-managed control data contains the MMIO base. Hardware mux values persist in MPP registers. There is no suspend/resume, no remove-time state handling, and no runtime PM.

Dependencies and integration points: dependencies are the MVEBU core, OF compatible matching, and one contiguous MPP MMIO resource. The driver integrates with legacy Kirkwood board DTS files and peripheral drivers through named pinctrl functions.

Risks and test signals: the variant mask table is dense and includes duplicate mux values with different names on different variants; table mistakes can silently expose the wrong function. Some variants use GPO where others use GPIO, affecting `gpio_set_direction()` support. Test each compatible's debugfs function list, GPIO ranges with holes and high pins, SDIO/SATA/LCD functions on 6282, switch variants 98DX4122/1135, and unsupported-function rejection on smaller 619x pin counts.
