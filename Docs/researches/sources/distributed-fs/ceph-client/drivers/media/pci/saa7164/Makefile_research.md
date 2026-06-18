# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Makefile

Purpose: builds the SAA7164 driver as a single composite object from card, core, I2C, DVB, firmware, bus, command, API, buffer, encoder, and VBI implementation files.

Important APIs, types, and functions: `saa7164-objs` lists all linked objects: `saa7164-cards.o`, `saa7164-core.o`, `saa7164-i2c.o`, `saa7164-dvb.o`, `saa7164-fw.o`, `saa7164-bus.o`, `saa7164-cmd.o`, `saa7164-api.o`, `saa7164-buffer.o`, `saa7164-encoder.o`, and `saa7164-vbi.o`. `obj-$(CONFIG_VIDEO_SAA7164) += saa7164.o` gates the module. Include flags expose tuner and DVB frontend headers.

Control flow: Kbuild compiles listed objects and links them into `saa7164.ko` or built-in code depending on the Kconfig symbol.

State and persistence: no runtime state; only build products.

Dependencies and integration points: include paths are required for tuner/frontend integration used by the DVB and board setup code. The object list defines which implementation files participate in the single module namespace.

Risks: omitting an object produces missing symbols or disabled functionality; stale include paths break builds when frontend headers move. Since all objects link into one module, global variables and symbols share a namespace.

Test signals: `make M=drivers/media/pci/saa7164`; inspect `saa7164.ko` symbol resolution; test both module and built-in configurations.
