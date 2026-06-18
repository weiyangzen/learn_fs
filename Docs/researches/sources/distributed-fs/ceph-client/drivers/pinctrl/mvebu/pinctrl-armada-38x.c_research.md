# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-38x.c

## Purpose
This file provides Marvell Armada 380/385/388 family MPP mode data and probe glue for the shared MVEBU pinctrl core, with variant masks for MV88F6810, MV88F6820, and MV88F6828 capabilities.

## Important APIs, Types, and Data
- Variant bits `V_88F6810`, `V_88F6820`, `V_88F6828`, and combined masks gate functions by SoC model.
- `armada_38x_mpp_modes` describes MPP pins 0-59 with `MPP_VAR_FUNCTION()` entries for GPIO, UART, I2C, GE/MDIO, PCIe, SPI, SATA presence, PTP, DRAM, SD0, device bus, NAND, TDM, audio, and reference clocks.
- `armada_38x_pinctrl_of_match` binds three compatibles and stores the corresponding variant bit in match data.
- `armada_38x_mpp_controls` declares one MMIO control range for pins 0-59.
- `armada_38x_mpp_gpio_ranges` exposes GPIO ranges 0-31 and 32-59.
- `armada_38x_pinctrl_probe()` reads variant match data, fills SoC info, and delegates to `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
Probe casts `device_get_match_data()` to the low 8-bit variant mask, populates the shared SoC info structure with controls/ranges/modes, stores it in platform data, and calls the shared simple MMIO probe. The shared core uses the variant mask to expose only valid functions for the matched SoC.

## State and Persistence
This file keeps static mode/control data and a static SoC info structure. MPP selections persist in hardware registers. No local runtime state or suspend/resume code is implemented here.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, `linux/property.h` for match data access, and OF platform matching. It is selected by `CONFIG_PINCTRL_ARMADA_38X`.

## Risks
Variant masks must be accurate; exposing an unsupported PCIe/SATA/GE function on a lower variant can mislead DT authors and fail hardware operation. Shared-core behavior depends on `soc->nmodes = armada_38x_mpp_controls[0].npins`, so the control range and table length must stay synchronized. Dense table entries for storage/network pins are boot-critical.

## Test Signals
Build and boot each supported compatible (`mv88f6810`, `mv88f6820`, `mv88f6828`), verify variant-filtered functions in debugfs, and test representative UART/I2C/SPI/SD/GE/PCIe/SATA/GPIO paths. Compile-time warnings around pointer-to-integer match-data casts should be watched.
