# sources/distributed-fs/ceph-client/drivers/net/mctp/Makefile

Purpose: Maps MCTP transport Kconfig symbols to object files for kbuild.

Important entries: `CONFIG_MCTP_SERIAL` builds `mctp-serial.o`, `CONFIG_MCTP_TRANSPORT_I2C` builds `mctp-i2c.o`, `CONFIG_MCTP_TRANSPORT_I3C` builds `mctp-i3c.o`, and `CONFIG_MCTP_TRANSPORT_USB` builds `mctp-usb.o`.

Control flow and integration: kbuild evaluates each `obj-$(CONFIG_...)` line and links the object into the kernel when the symbol is `y` or builds a module when the symbol is `m`. The symbols are defined in the adjacent `Kconfig`, so this file is the final build integration for the transport drivers.

State and persistence: There is no runtime state. The Makefile only persists the source-to-object mapping used by kernel builds.

Risks and test signals: Risks are symbol/object name drift, missing objects after adding Kconfig options, or module naming surprises. Test by building each transport as built-in and module where dependencies permit and confirming the expected object/module names are produced.
