# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/Makefile

## Purpose
This Makefile declares the Linux kernel build objects for the Chelsio T3 `cxgb3` driver.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CHELSIO_T3) += cxgb3.o` builds the module/object when the kernel config enables Chelsio T3.
- `cxgb3-objs` links `cxgb3_main.o`, PHY drivers (`ael1002.o`, `vsc8211.o`, `aq100x.o`), hardware setup (`t3_hw.o`, `mc5.o`, `xgmac.o`), SGE (`sge.o`), L2 table (`l2t.o`), and offload support (`cxgb3_offload.o`) into `cxgb3.o`.

## Control Flow And State
There is no runtime control flow. The file controls build-time composition of the driver.

## Dependencies And Integration Points
The object list establishes integration between the main PCI/netdev driver, T3 hardware module code, PHY implementations, MAC, SGE DMA queues, Layer 2 table, and offload control path. It depends on the kernel Kbuild system and `CONFIG_CHELSIO_T3`.

## Risks And Edge Cases
Leaving an object out can produce missing symbols or silently omit a PHY/offload path. Adding an object without matching config dependencies can break builds. Object ordering is mostly link-time composition, but symbol availability must match declarations in shared headers such as `common.h` and `adapter.h`.

## Test Signals
The primary signal is a successful kernel/module build with `CONFIG_CHELSIO_T3=y/m`, followed by successful probe paths for boards requiring each listed PHY object and offload path.
