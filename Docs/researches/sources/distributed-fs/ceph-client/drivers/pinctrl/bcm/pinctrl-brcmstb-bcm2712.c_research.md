<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb-bcm2712.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb-bcm2712.c

## Purpose
This file supplies BCM2712-specific data for the generic Broadcom STB pinctrl core. It describes C0 and D0 silicon variants, normal and always-on pin banks, register bit locations, GPIO ranges, function names, and per-pin alternate-function tables.

## Important APIs, Types, And Functions
`enum bcm2712_funcs` defines the symbolic function IDs used by the shared brcmstb core. `BRCMSTB_PIN()` builds per-pin arrays of up to eight alternate functions plus mask metadata. `bcm2712_*_pin_regs` map each pin number to mux and pad bits through macros from `pinctrl-brcmstb.h`. `bcm2712_*_pins` define normal GPIO, eMMC, AON GPIO, and AON SGPIO pin descriptors. Four `struct brcmstb_pdata` instances bind descriptors, ranges, register maps, function maps, and function-name arrays for C0, C0 AON, D0, and D0 AON variants.

## Control Flow
The local probe is a thin wrapper around `brcmstb_pinctrl_probe()`. OF match data selects the correct `brcmstb_pdata` for `brcm,bcm2712c0-pinctrl`, `brcm,bcm2712c0-aon-pinctrl`, `brcm,bcm2712d0-pinctrl`, or `brcm,bcm2712d0-aon-pinctrl`. The shared brcmstb core then uses the tables here to register pinctrl and program mux or bias bits.

## State And Persistence
This data file stores no mutable runtime state. Its tables are immutable descriptions of hardware layout. The actual mux and pull state persists in BCM2712 pin controller registers handled by `pinctrl-brcmstb.c`.

## Dependencies And Integration Points
Depends on `pinctrl-brcmstb.h` macros and `brcmstb_pinctrl_probe()`. It integrates BCM2712 board DT compatible strings with the shared brcmstb pinctrl logic and exposes function names for peripherals including SD/eMMC, Ethernet, UART, SPI, I2C, PWM, HDMI, I2S, PDM, JTAG, USB power/vbus, and AON functions.

## Risks
The risk is table accuracy. Each pin has independent mux and pad bit locations, and D0 removes or shifts several pins relative to C0. A wrong function ID, register bit, or range count can route a peripheral to the wrong pad or expose a non-existent pin. eMMC pins have no mux bit and only pad control, which the core treats specially.

## Test Signals
Validate pinctrl states on BCM2712 C0 and D0 boards for normal and AON controllers. Check eMMC pad bias, GPIO and SGPIO function selection, UART/I2C/SPI/SD/Ethernet alternate routes, and debugfs pin function names. Probe should bind separately for normal and AON compatible nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb-bcm2712.c -->
