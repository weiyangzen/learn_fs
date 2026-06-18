<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Makefile

Purpose: builds the Xilinx AXI-Stream FIFO staging driver object when enabled.

Important APIs/types/functions: `obj-$(CONFIG_XIL_AXIS_FIFO) += axis-fifo.o`.

Control flow: kbuild includes the object for built-in or module output based on the tristate symbol.

State and persistence: no runtime state.

Dependencies and integration: tied directly to `axis-fifo/Kconfig` and the top-level staging Makefile.

Risks: any source rename or Kconfig symbol rename must be reflected here or the driver will not build.

Test signals: build with `CONFIG_XIL_AXIS_FIFO=y` and `m` and verify `axis-fifo.o`/module output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Makefile -->
