# sources/distributed-fs/ceph-client/drivers/net/mctp/Kconfig

Purpose: Defines Kconfig options for MCTP transport device drivers under the `if MCTP` menu. It exposes serial, SMBus/I2C, I3C, and USB transports plus a KUnit test option for the serial binding.

Important options: `MCTP_SERIAL` is a tristate line-discipline transport depending on `TTY` and selecting `CRC_CCITT`; its module name is `mctp-serial`. `MCTP_SERIAL_TEST` is a bool enabled by `KUNIT_ALL_TESTS` when serial is built-in with KUnit. `MCTP_TRANSPORT_I2C` is a tristate SMBus/I2C binding depending on `I2C`, `I2C_SLAVE`, and `I2C_MUX || !I2C_MUX`, and selects `MCTP_FLOWS`. `MCTP_TRANSPORT_I3C` depends on `I3C`. `MCTP_TRANSPORT_USB` depends on `USB`.

Control flow and integration: Kconfig does not execute runtime code; it controls which transport objects the Makefile builds. The outer `if MCTP` ensures the menu is visible only when the MCTP core is enabled. Help text documents the DMTF binding specifications and expected netdevice creation model for each bus.

State and persistence: The file contributes build-time configuration state only. Selected tristates determine built-in versus module artifacts, and dependencies prevent impossible combinations such as I2C transport without I2C slave support.

Dependencies and risks: The I2C mux dependency is intentionally shaped so the transport cannot be built-in when `i2c-mux` is modular. Risks are dependency drift with core bus APIs, stale help text/module names, and missing test coverage for modular/built-in combinations.

Test signals: Build matrix coverage should include MCTP disabled, each transport as built-in/module where legal, `MCTP_SERIAL_TEST` under KUnit, I2C mux built-in/module permutations, and all transports together.
