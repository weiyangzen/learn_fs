# sources/distributed-fs/ceph-client/drivers/misc/keba/Kconfig

## Purpose
This Kconfig fragment exposes KEBA CP500 system FPGA support and the KEBA LAN9252 configuration helper.

## Important APIs, types, and functions
`CONFIG_KEBA_CP500` is a tristate option for the PCI system FPGA driver. It depends on `X86_64 || ARM64 || COMPILE_TEST`, `PCI`, and `I2C`, and selects `AUXILIARY_BUS`. `CONFIG_KEBA_LAN9252` is a tristate option for the SPI LAN9252 configuration driver. It depends on `SPI` and either `KEBA_CP500` or `COMPILE_TEST`.

## Control flow
The file participates in kernel configuration only. Selecting CP500 enables compilation of the PCI parent that registers auxiliary subdevices. Selecting LAN9252 enables the SPI child driver used when the CP500 EEPROM indicates a LAN9252 EtherCAT slave controller.

## State and persistence
No runtime state is stored here. The selected configuration controls whether `cp500.o` and `lan9252.o` can be built as built-ins or modules.

## Dependencies and integration points
The dependency graph mirrors runtime integration: CP500 needs PCI and I2C/nvmem-discovered EEPROMs, and LAN9252 needs an SPI master plus either the CP500 platform or compile-test coverage.

## Risks
Incorrect dependencies would allow builds without required subsystem symbols or hide valid hardware support. `AUXILIARY_BUS` selection is required because `cp500.c` publishes child devices using auxiliary-device APIs.

## Test signals
Kconfig tests should cover built-in, module, disabled, and `COMPILE_TEST` combinations on x86_64 and arm64. Build output should produce `cp500.ko` and/or `lan9252.ko` under the expected option names.
