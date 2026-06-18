# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Makefile

Purpose: this Makefile maps XRS700x Kconfig symbols to the objects built by kbuild.

Important APIs, types, and functions: `obj-$(CONFIG_NET_DSA_XRS700X) += xrs700x.o` builds the common DSA core, `obj-$(CONFIG_NET_DSA_XRS700X_I2C) += xrs700x_i2c.o` builds the I2C frontend, and `obj-$(CONFIG_NET_DSA_XRS700X_MDIO) += xrs700x_mdio.o` builds the MDIO frontend.

Control flow: Kconfig transport selections determine which object files are linked into the kernel or built as modules. The core is selected by each transport and therefore accompanies any frontend.

State and persistence: there is no runtime state; this file only controls build artifacts.

Dependencies and integration points: it relies on the Kconfig symbols in the same directory and on source files that export/import the common core APIs declared by `xrs700x.h`.

Risks: if a transport selects the core as built-in while another is modular, kbuild combinations need to preserve symbol availability. The Makefile references `xrs700x_mdio.o`, so source presence outside this work item is required for MDIO builds.

Test signals: build the driver as built-in and module for I2C, MDIO, and combined configurations, and verify module dependency ordering for `xrs700x`, `xrs700x_i2c`, and `xrs700x_mdio`.
