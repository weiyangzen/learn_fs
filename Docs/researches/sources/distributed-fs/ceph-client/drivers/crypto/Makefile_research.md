<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/Makefile

## Purpose

`drivers/crypto/Makefile` maps hardware crypto Kconfig symbols to object files and vendor subdirectories.

## Important APIs, Types, And Functions

It includes direct objects such as `geode-aes.o`, `hifn_795x.o`, `mxs-dcp.o`, `padlock-aes.o`, `qcom-rng.o`, `s5p-sss.o`, `sa2ul.o`, and `talitos.o`, plus subdirectories such as `allwinner/`, `ccp/`, `caam/`, `marvell/`, `qce/`, `rockchip/`, `tegra/`, `virtio/`, `intel/`, `xilinx/`, and others. It also composes `omap-aes-driver-objs` from `omap-aes.o` and `omap-aes-gcm.o`.

## Control Flow

There is no runtime flow. Kbuild uses the `obj-$(CONFIG_...)` assignments to include built-in objects or modules. Some directories are always visited with `obj-y` because their own Kconfig/Makefiles decide which children build.

## State And Persistence Behavior

The Makefile owns no runtime state; it controls the build graph that determines module names and linked objects.

## Dependencies And Integration Points

It integrates top-level crypto Kconfig symbols with individual driver source directories and compound object definitions.

## Risks And Test Signals

Risks include stale object names, missing new driver directories, incorrect always-built subdirectories, and compound object ordering problems such as the explicit Atmel I2C init ordering note. Test with allmodconfig, allyesconfig, and targeted module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Makefile -->
