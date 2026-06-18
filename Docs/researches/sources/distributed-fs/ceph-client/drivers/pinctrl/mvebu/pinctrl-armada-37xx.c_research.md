# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-37xx.c

## Purpose
This is a custom pinctrl, pinmux, GPIO, GPIO-IRQ, and power-management driver for Marvell Armada 37xx north-bridge and south-bridge pin controllers. Unlike older MVEBU table drivers, it does not use `pinctrl-mvebu.c`; it builds functions/groups dynamically from local group tables and directly manages GPIO and interrupt registers.

## Important APIs, Types, and Functions
- Register offsets define GPIO output enable/input/output/control, mux selection, IRQ enable/polarity/status/wakeup.
- `struct armada_37xx_pin_group` describes contiguous and optional extra pin ranges, mux mask/value choices, supported function names, and allocated pin lists.
- `struct armada_37xx_pin_data` describes NB or SB controller instances.
- `struct armada_37xx_pmx_func` is built dynamically from group function names.
- `struct armada_37xx_pm_state` saves GPIO, IRQ, and selection state across suspend.
- NB/SB group tables define functions such as JTAG, SDIO, eMMC, PWM/LED, PMIC, I2C, SPI, UART, one-wire, USB drive-vbus, RGMII/MII/SMI, PCIe, and PTP.
- Pinctrl ops expose group metadata; pinconf group get/set are unsupported.
- Pinmux ops implement function enumeration, group lookup, mux setting, GPIO request enable, and GPIO direction setting.
- GPIO callbacks implement direction, get, and set.
- IRQ chip callbacks implement ack, mask/unmask, wake, type setup, startup, print, both-edge polarity swapping, chained handling, and registration.
- `armada_37xx_pinctrl_register()` creates pin descriptors, fills group/function arrays, and registers pinctrl.
- Suspend/resume saves and restores GPIO, IRQ, and mux selection state, including both-edge IRQ polarity resynchronization.
- `armada_37xx_pinctrl_probe()` maps resources, creates regmap, registers pinctrl and GPIO chip, and stores driver data.

## Control Flow
Probe maps resource 0 for pinctrl registers, creates a raw-spinlock-enabled regmap, selects NB or SB pin data from DT match data, registers pinctrl, registers a GPIO chip, and optionally wires parent IRQs from the GPIO child node. During pinctrl registration, groups allocate concrete pin arrays and unique functions are counted, then each function gets its list of groups. Mux selection writes `SELECTION` bits using the selected group mask/value. GPIO requests force every group containing the pin into its `gpio` function. GPIO operations read/write register banks with `armada_37xx_update_reg()` to handle low/high register halves. IRQ handling scans enabled status bits, optionally flips polarity for both-edge emulation, and dispatches mapped child IRQs.

## State and Persistence
Runtime state is held in `struct armada_37xx_pinctrl`, including dynamically allocated functions, group pin arrays, gpio chip, IRQ lock, regmap, IRQ base, and saved PM state. Hardware register state persists until changed; suspend stores output enable/value, IRQ enable/polarity, and selection, then resume restores them and repairs both-edge polarity using current input levels.

## Dependencies and Integration Points
The driver depends on Linux pinctrl, pinmux, generic pinconf mapping, gpiolib, GPIO IRQ helpers, OF IRQ parsing, platform MMIO resources, regmap, and device PM. It binds `marvell,armada3710-sb-pinctrl` and `marvell,armada3710-nb-pinctrl`, expecting GPIO child-node information for gpiolib and optional parent interrupts.

## Risks
Pinconf is effectively unsupported despite generic pinconf ops being registered; DT users expecting electrical configuration will not get it here. Both-edge IRQ support is implemented by polarity toggling and depends on input-level races being handled correctly. `armada_37xx_irq_handler()` loops through `d->revmap_size / GPIO_PER_REG` inclusively, so bounds should be validated against actual domain sizes. `armada_37xx_gpio_direction_output()` reuses the output-value mask for output-enable after recomputing the register with a separate offset; this works only because the low/high bit index is equivalent, and should be treated carefully in modifications. IRQ registration returns success when no parent IRQ exists, leaving GPIO usable without interrupts.

## Test Signals
Boot NB and SB instances, verify pinctrl group/function enumeration, request GPIO on pins that belong to alternate groups, and test GPIO direction/value across pins below and above 32. IRQ tests should cover rising, falling, both-edge, wake enable, masked status filtering, and suspend/resume with changing input levels. PM tests should confirm mux selection and GPIO outputs survive suspend.
