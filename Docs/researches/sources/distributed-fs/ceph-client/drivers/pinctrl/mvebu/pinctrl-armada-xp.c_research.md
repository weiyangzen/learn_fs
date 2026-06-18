# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-xp.c

Purpose: this file supports Armada XP and related 98DX switch SoC pinmuxing. It handles mv78230 with 49 pins, mv78260/mv78460 with 67 pins, and 98DX3236/3336/4251-style devices with a separate 33-pin table.

Important APIs, types, and functions: `armada_xp_mpp_modes[]` defines the Armada XP table, while `mv98dx3236_mpp_modes[]` defines the switch-family table. Variant masks include `V_MV78230_PLUS`, `V_MV78260_PLUS`, and `V_98DX3236_PLUS`. Per-variant `mvebu_mpp_ctrl` and `pinctrl_gpio_range` arrays describe pin count and GPIO range splits. `armada_xp_pinctrl_probe()` selects the table/ranges by compatible. `armada_xp_pinctrl_suspend()` and `armada_xp_pinctrl_resume()` save and restore raw MPP registers through `mpp_saved_regs`.

Control flow: OF match provides a variant. Probe selects controls, modes, GPIO ranges, computes the number of MPP registers, allocates the save buffer, attaches SoC info as platform data, and uses the simple MMIO probe. Runtime muxing is shared-core nibble read/write. Legacy platform suspend reads each MPP register from the first control base; resume writes the saved values back.

State and persistence behavior: the selected SoC info is stored in a static `armada_xp_pinctrl_info`, and suspend state is held in the global `mpp_saved_regs` buffer allocated for the probed device. Hardware muxing persists in MMIO registers but can be restored after suspend. The global buffer/static info design assumes one active instance.

Dependencies and integration points: dependencies are MMIO MPP registers, platform PM callbacks, the MVEBU pinctrl core, and DTS compatibles. Integrations include Ethernet, LCD, SPI, SDIO, UART, TDM, SATA presence/activity, PCIe clock/reset, NAND/device bus, and switch-specific SMI/dev pins.

Risks and test signals: the static save buffer and static SoC info are not multi-instance friendly. Suspend/resume assumes `soc->control_data[0].base` is valid and that `soc->nmodes` maps to contiguous 4-bit registers. Variant table correctness is important because some pins are GPO only and some 98DX4251-only SDIO functions share values with other functions. Test each compatible, GPIO ranges at 0/32/64 boundaries, switch-family GPO behavior, and suspend/resume register restoration.
