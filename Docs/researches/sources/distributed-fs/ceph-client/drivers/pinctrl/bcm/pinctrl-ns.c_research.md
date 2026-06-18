<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns.c

## Purpose
This file implements the Broadcom Northstar pinmux driver for BCM4708, BCM4709, and BCM53012. It filters the static pin/group/function tables by chipset compatible and programs the CRU GPIO control register to enable peripheral functions.

## Important APIs, Types, And Functions
`struct ns_pinctrl` stores the device, chipset flag, pinctrl device, mapped CRU register base, and descriptor copy. `ns_pinctrl_pins`, `ns_pinctrl_groups`, and `ns_pinctrl_functions` carry chipset masks in descriptor or table metadata. `ns_pinctrl_set_mux()` resolves the generic group and clears bits for all pins in the group in the control register.

## Control Flow
Probe determines the chipset flag from OF match data, maps the named `cru_gpio_control` resource, copies the base descriptor, filters supported pins into a device-managed descriptor array, registers pinctrl, and then adds only supported groups and functions to the generic registries. Applying a pinctrl state calls the generic function/group flow and then `ns_pinctrl_set_mux()`, which clears the relevant pin bits in the CRU GPIO control register.

## State And Persistence
The runtime state is the chipset flag, descriptor copy, pinctrl device, and MMIO base. Hardware mux state persists in the CRU GPIO control register. There is no GPIO, IRQ, or pinconf state in this driver.

## Dependencies And Integration Points
Depends on generic pinctrl/pinmux helpers, OF match data, named MMIO resources, and DT group mapping through `pinconf_generic_dt_node_to_map_group()`. It binds to `brcm,bcm4708-pinmux`, `brcm,bcm4709-pinmux`, and `brcm,bcm53012-pinmux`.

## Risks
The driver only clears bits for selected groups; the register's polarity and reset state must match the hardware contract. Chipset filtering must remain consistent between pins, groups, and functions or generic pinmux may expose a function whose pins were filtered out. There is no lock around the single read/modify/write register update, which is acceptable only if pinctrl state changes are serialized by higher layers.

## Test Signals
Test each compatible variant to ensure unsupported MDIO/UART2/SDIO pins are absent on BCM4708 and present on BCM4709/BCM53012. Apply SPI, I2C, MDIO, PWM, UART1, UART2, and SDIO states and verify CRU register bits and peripheral operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns.c -->
