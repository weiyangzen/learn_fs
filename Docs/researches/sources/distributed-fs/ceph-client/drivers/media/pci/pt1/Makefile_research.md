# sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Makefile

Purpose: Kbuild metadata for the Earthsoft PT1/PT2 driver.

Important APIs, types, and functions: `earth-pt1-objs := pt1.o` declares a composite object even though it currently has one source. `obj-$(CONFIG_DVB_PT1) += earth-pt1.o` ties it to Kconfig. Include flags add DVB frontend and tuner directories.

Control flow: Build-time only.

State and persistence: No runtime state.

Dependencies and integration points: Include paths support local includes for `tc90522.h`, `qm1d1b0004.h`, and `dvb-pll.h`.

Risks: Future source splits require updating `earth-pt1-objs`. The object name differs from the directory and config symbol, so packaging/tests should check for `earth-pt1`.

Test signals: Build with `CONFIG_DVB_PT1=y/m`, verify include paths and module naming, and run dependency builds with frontend/tuner headers moved or disabled.
