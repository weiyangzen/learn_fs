# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Makefile`.

Important APIs and functions: declarative build entries include `obj-y		+= clk.o cpu.o cs.o gpio.o irq.o nvram.o prom.o reset.o \; obj-$(CONFIG_EARLY_PRINTK)	+= early_printk.o; obj-y		+= boards/`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
