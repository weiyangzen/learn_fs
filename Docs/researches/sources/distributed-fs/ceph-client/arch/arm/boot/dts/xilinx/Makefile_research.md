<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/Makefile

## Purpose
Kbuild manifest for Xilinx Zynq ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_ZYNQ)` lists ZC702/ZC706/ZC770 variants, MicroZed, ZedBoard, Zybo, Z-turn, Parallella, EBAZ4205, and related Zynq boards.

## Control flow
Kbuild includes all listed Zynq DTBs when `CONFIG_ARCH_ZYNQ` is enabled.

## State and persistence behavior
No runtime state. It persists the Zynq DTB target set and names expected by board boot flows.

## Dependencies and integration points
Depends on Zynq DTS files, the Zynq Kconfig symbol, DTC, and Xilinx platform binding schemas.

## Risks and edge cases
Board revisions with similar names can be easy to confuse. Missing DTB entries reduce board coverage; stale names break `dtbs`.

## Test signals
Run `make ARCH=arm dtbs` with Zynq enabled and `make ARCH=arm dtbs_check` for Zynq boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/Makefile -->
