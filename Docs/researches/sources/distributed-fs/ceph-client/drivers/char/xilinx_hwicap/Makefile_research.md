<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/Makefile

Purpose: Kbuild fragment for the Xilinx HWICAP character driver.

Important APIs/types/functions: It builds `xilinx_hwicap_m.o` when `CONFIG_XILINX_HWICAP` is enabled and composes that module from `xilinx_hwicap.o`, `fifo_icap.o`, and `buffer_icap.o`.

Control flow: no runtime control flow; this file only declares object composition for the kernel build.

State and persistence: no runtime state. Build state is determined by Kconfig symbol selection.

Dependencies and integration: integrates the common char-device layer with both FIFO-backed and BRAM-buffer-backed ICAP transport implementations.

Risks: object ordering must continue to include both backend implementations because `xilinx_hwicap.c` references both config tables. The target name `xilinx_hwicap_m` controls the module object name and must match surrounding Kbuild expectations.

Test signals: build with `CONFIG_XILINX_HWICAP=y` and `=m`, verify all three objects link, and boot/probe a matching Device Tree node for both compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/Makefile -->
