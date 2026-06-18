# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/Makefile

## Purpose
This Makefile defines the object composition for the Chelsio T1 `cxgb` driver. It builds `cxgb.o` when `CONFIG_CHELSIO_T1` is enabled and conditionally adds one-gigabit PHY/MAC support objects when `CONFIG_CHELSIO_T1_1G` is enabled.

## Important Rules
`obj-$(CONFIG_CHELSIO_T1) += cxgb.o` declares the module/built-in target. `cxgb-$(CONFIG_CHELSIO_T1_1G) += mv88e1xxx.o vsc7326.o` conditionally adds gigabit support. `cxgb-objs := cxgb2.o espi.o tp.o pm3393.o sge.o subr.o mv88x201x.o my3126.o $(cxgb-y)` defines the core T1 object list.

## Control Flow and Integration
Kbuild combines the listed objects into one `cxgb` driver. Core files cover adapter entry, ESPI, TP, PM3393 MAC, SGE, support routines, and 10G PHYs; optional `cxgb-y` contributes gigabit PHY/switch objects. The parent Chelsio Makefile enters this directory based on `CONFIG_CHELSIO_T1`.

## State and Persistence
The file has no runtime state. Build state is the selected object set in the generated kernel build tree.

## Dependencies and Risks
Risks include object order assumptions, optional one-gigabit symbols not being compiled when code references them, and stale object names after source moves. Because everything links into one module, missing optional guards surface as link failures.

## Test Signals
Build `CONFIG_CHELSIO_T1=m/y` with `CONFIG_CHELSIO_T1_1G=y` and `n`, inspect `cxgb.o` composition, and verify no undefined references from optional gigabit support.
