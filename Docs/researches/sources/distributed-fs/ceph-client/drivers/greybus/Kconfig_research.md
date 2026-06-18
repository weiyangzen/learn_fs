# sources/distributed-fs/ceph-client/drivers/greybus/Kconfig

Purpose: configuration menu for Greybus core and host-controller drivers.

Important symbols: `GREYBUS` is a tristate depending on SYSFS. `GREYBUS_BEAGLEPLAY` depends on SERIAL_DEV_BUS and selects CRC_CCITT, FW_LOADER, and FW_UPLOAD. `GREYBUS_ES2` depends on USB.

Control flow: no runtime flow; symbols control module compilation.

State and persistence: no state.

Dependencies and integration: enables the Greybus core module, BeaglePlay CC1352 SVC transport, and Toshiba ES3 USB host controller bridge.

Risks: transport-specific symbols pull in firmware and serial/USB dependencies. Users may enable Greybus core without a host controller, yielding no functional bus.

Test signals: expected modules build as `greybus.ko`, `gb-beagleplay.ko`, and `gb-es2.ko` depending on configuration.
