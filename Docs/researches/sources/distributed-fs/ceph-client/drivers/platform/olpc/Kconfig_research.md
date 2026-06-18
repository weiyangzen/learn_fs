# sources/distributed-fs/ceph-client/drivers/platform/olpc/Kconfig

Purpose: Kconfig definitions for OLPC embedded-controller platform support, especially the ARM-based XO-1.75 family.

Important APIs, types, and functions: `config OLPC_EC` is an internal boolean selecting `REGULATOR`; `menuconfig OLPC_XO175` exposes platform support for `ARCH_MMP` or `COMPILE_TEST`; `config OLPC_XO175_EC` builds the SPI slave EC driver and depends on `SPI_SLAVE`, `INPUT`, and `POWER_SUPPLY`, while selecting `OLPC_EC`.

Control flow: this file is evaluated by Kconfig. Enabling `OLPC_XO175_EC` selects the generic OLPC EC layer and makes both `olpc-ec.o` and `olpc-xo175-ec.o` available through the Makefile.

State and persistence: configuration state is persisted in the kernel `.config`. No runtime state is declared here.

Dependencies and integration points: ties platform support to ARM MMP or compile testing, SPI target/slave support, input power-button reporting, power-supply notifications, and the regulator framework via the generic EC layer.

Risks: `OLPC_EC` is a bool selected by `OLPC_XO175_EC`; if other OLPC EC transports need it, dependencies must ensure the generic object is built in a compatible link mode. Missing `SPI_SLAVE`, `INPUT`, or `POWER_SUPPLY` prevents the XO-1.75 EC driver from appearing.

Test signals: run `make olddefconfig`/`menuconfig` combinations for `ARCH_MMP`, `COMPILE_TEST`, built-in and module variants of `OLPC_XO175_EC`, and verify selected objects and dependencies are consistent.
