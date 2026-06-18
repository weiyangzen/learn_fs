# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-39x.c

Purpose: this file is the Armada 39x SoC table driver for the shared MVEBU pinctrl core. It describes the 60 MPP pins on mv88f6920, mv88f6925, and mv88f6928 devices and maps each pin's 4-bit mux value to functions such as GPIO, UART, I2C, SPI, SDIO, SMI/XSMI, SATA presence, PCIe reset/clock request, GE, LED, TDM, audio, NAND, and DRAM signals.

Important APIs, types, and functions: the central data is `armada_39x_mpp_modes[]`, built from `MPP_MODE()` and `MPP_VAR_FUNCTION()` entries with variant masks `V_88F6920`, `V_88F6925`, and `V_88F6928`. `armada_39x_mpp_controls[]` exposes pins 0-59 as one unnamed `mvebu_mmio_mpp_ctrl` range, so the core creates one group per pin (`mpp0` ... `mpp59`). `armada_39x_mpp_gpio_ranges[]` registers two GPIO ranges. `armada_39x_pinctrl_probe()` fills `mvebu_pinctrl_soc_info` and calls `mvebu_pinctrl_simple_mmio_probe()`.

Control flow: the builtin platform driver matches one of three compatible strings, derives the variant from `device_get_match_data()`, installs the static controls, modes, and GPIO ranges as platform data, maps the single MMIO resource through the shared helper, and delegates registration to `mvebu_pinctrl_probe()`. Runtime mux requests are handled entirely by the core: DT `marvell,function` plus `marvell,pins` maps to a setting, and the core writes the selected nibble through `mvebu_mmio_mpp_ctrl_set()`.

State and persistence behavior: there is no private runtime state beyond the shared static `armada_39x_pinctrl_info` and the device-managed MMIO control-data array allocated by the simple probe helper. Pin state persists in the hardware MPP registers until changed by pinctrl or reset. There is no suspend/resume save path in this file.

Dependencies and integration points: this driver depends on the MVEBU pinctrl core, platform/OF matching, MMIO resource mapping, and Linux pinctrl/GPIO range registration. Consumers are board DTS pinctrl nodes using function names exactly as listed in the table.

Risks and test signals: the main risk is table correctness. Variant masks gate SATA, TDM, audio, and higher-end pins, so the same DTS can be accepted or rejected depending on compatible. `soc->nmodes` is set from the control pin count, which assumes a one-to-one mode table for pins 0-59. Test by booting each compatible, applying representative UART/I2C/SPI/SDIO/GE/SATA/PCIe muxes, checking debugfs available functions, and verifying GPIO ranges 0-31 and 32-59.
