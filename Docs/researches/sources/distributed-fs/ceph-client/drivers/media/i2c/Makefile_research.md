# sources/distributed-fs/ceph-client/drivers/media/i2c/Makefile

Purpose: Kbuild object list for media I2C V4L2 subdevice drivers.

Important APIs/types/functions: Maps Kconfig symbols to objects and subdirectories. Relevant subset mappings are `CONFIG_VIDEO_AD5820 -> ad5820.o`, `CONFIG_VIDEO_ADP1653 -> adp1653.o`, `CONFIG_VIDEO_ADV7170 -> adv7170.o`, and `CONFIG_VIDEO_ADV7175 -> adv7175.o`. It also defines composite `msp3400-objs` and routes large drivers like `adv748x/`, `ccs/`, and `cx25840/` into subdirectories.

Control flow: Kbuild includes each object according to the resolved tristate. Directory entries delegate to nested Makefiles. Object order is mostly a flat list and does not encode runtime ordering.

State and persistence: No runtime state. The file defines link-time module composition.

Dependencies/integration: Consumes the symbols declared in `drivers/media/i2c/Kconfig` and must stay in sync with source filenames and module names.

Risks and test signals: Build with each relevant Kconfig symbol as module and built-in, confirm object names match source files, and audit additions/removals so stale entries do not break allmodconfig or leave Kconfig options without build products.
