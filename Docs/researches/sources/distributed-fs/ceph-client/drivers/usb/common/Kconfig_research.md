# Research: sources/distributed-fs/ceph-client/drivers/usb/common/Kconfig

Purpose: declares Kconfig symbols for USB common support and small common USB facilities. `USB_COMMON` is the shared tristate selected by host/gadget/common helpers. `USB_LED_TRIG` enables USB activity LED triggers. `USB_ULPI_BUS` enables the ULPI PHY bus implementation. `USB_CONN_GPIO` enables GPIO-based USB role/connection detection.

Important symbols: `USB_COMMON` is a bare tristate used as a build target. `USB_LED_TRIG` is a bool depending on `LEDS_CLASS`, `USB_COMMON`, and `LEDS_TRIGGERS`. `USB_ULPI_BUS` is tristate, selects `USB_COMMON`, and builds module `ulpi`. `USB_CONN_GPIO` is tristate, depends on `GPIOLIB`, selects `USB_ROLE_SWITCH` and `POWER_SUPPLY`, and builds `usb-conn-gpio.ko`.

Control flow and state: Kconfig has no runtime control flow. The important behavior is dependency propagation into the Makefile: enabled symbols decide whether `common.o`, `debug.o`, `led.o`, `ulpi.o`, `usb-conn-gpio.o`, and `usb-otg-fsm.o` are compiled.

Dependencies and integration points: integrates with LED triggers, PHY/ULPI controller drivers, GPIO descriptor APIs, USB role switch, and power-supply class. `USB_OTG_FSM` is not declared here but is consumed by the common Makefile, with the actual option declared in the USB core Kconfig.

Risks: dependency changes can alter module boundaries and link availability for exported helpers. `USB_LED_TRIG` is bool rather than tristate, so its code is folded into `usb-common` rather than becoming a standalone module. `USB_CONN_GPIO` selecting role switch and power supply can pull extra subsystems into embedded builds.

Test signals: verify `allyesconfig`, `allmodconfig`, minimal host-only, gadget-only, `USB_ULPI_BUS=m`, and `USB_CONN_GPIO=m` builds. Confirm resulting modules and selected dependencies match the help text.
