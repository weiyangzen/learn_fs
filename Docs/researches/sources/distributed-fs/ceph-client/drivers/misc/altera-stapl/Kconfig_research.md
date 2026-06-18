# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Kconfig

Purpose: declares the `ALTERA_STAPL` kernel configuration option for the Altera FPGA firmware download module.

Important APIs and symbols: `ALTERA_STAPL` is a tristate named "Altera FPGA firmware download module". It depends on `I2C`. A comment is shown when I2C is unavailable.

Control flow: selecting this symbol enables kbuild to compile the STAPL interpreter, decompressor, and JTAG support through the local Makefile. The resulting module provides the firmware execution helper exported by `altera.c`.

State and persistence: no runtime state is stored here. The selected tristate persists in the kernel build configuration and controls whether the module is built in, modular, or absent.

Dependencies and integration points: integrates into the misc driver Kconfig tree and requires I2C even though the optional legacy parallel-port JTAG fallback is gated separately by `CONFIG_HAS_IOPORT` in the Makefile.

Risks: the help text is minimal and does not explain that the module interprets firmware bytecode and drives board-specific JTAG callbacks. Users may enable it without the board driver that supplies `struct altera_config`.

Test signals: menuconfig visibility with and without I2C, allmodconfig build coverage, and module build confirmation for `CONFIG_ALTERA_STAPL=m`.
