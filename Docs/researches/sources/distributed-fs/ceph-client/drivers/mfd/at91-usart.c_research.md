<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/at91-usart.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/at91-usart.c

Purpose: provides a mode-selecting MFD wrapper for AT91 USART blocks that can operate either as a serial controller or as an SPI controller. It creates exactly one child device based on the `atmel,usart-mode` firmware property.

Important APIs and functions: `at91_usart_mode_probe` reads the mode and calls `devm_mfd_add_devices`. Child cells are `"at91_usart_spi"` for `AT91_USART_MODE_SPI` and `"atmel_usart_serial"` for `AT91_USART_MODE_SERIAL`.

Control flow: probe defaults to serial mode if `atmel,usart-mode` is absent. It switches on the resulting value, rejects unknown modes with `-EINVAL`, and registers the selected child with automatic platform ID.

State and persistence: this wrapper keeps no private state. The selected child driver owns the hardware registers and runtime state after MFD creation.

Dependencies and integration points: depends on AT91 USART DT binding constants, device properties, OF platform matching for AT91 USART compatibles, and MFD core. It is the arbitration point that prevents both serial and SPI children from binding to the same hardware instance.

Risks: an omitted property silently selects serial mode, which is compatible with legacy bindings but can hide firmware mistakes. The wrapper does not validate pinctrl or clock resources; failures appear in the child driver. Changing mode at runtime is not supported.

Test signals: DT probe with absent, serial, SPI, and invalid `atmel,usart-mode` values; child driver binding for serial/SPI; and build coverage for both AT91 USART child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/at91-usart.c -->
