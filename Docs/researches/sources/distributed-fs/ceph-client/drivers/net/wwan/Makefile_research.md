# sources/distributed-fs/ceph-client/drivers/net/wwan/Makefile

## Purpose
Maps WWAN Kconfig symbols to object files and subdirectories for the top-level WWAN driver directory.

## Important APIs, Types, And Functions
Build rules include `obj-$(CONFIG_WWAN) += wwan.o`, `wwan-objs += wwan_core.o`, and conditional objects for `wwan_hwsim.o`, `mhi_wwan_ctrl.o`, `mhi_wwan_mbim.o`, `qcom_bam_dmux.o`, `rpmsg_wwan_ctrl.o`, `iosm/`, and `t7xx/`.

## Control Flow
Kbuild includes objects according to the resolved configuration. When `CONFIG_IOSM` is enabled, Kbuild descends into `drivers/net/wwan/iosm/`.

## State And Persistence
No runtime state. Build outputs and module composition are determined by these rules.

## Dependencies And Integration Points
Integrates with the Kconfig symbols in the same directory and each driver's source subtree.

## Risks
Object names must match source files and module expectations. Missing subdirectory rules would make enabled Kconfig options produce no driver.

## Test Signals
Run `make M=drivers/net/wwan` or equivalent targeted kernel builds under configs enabling each symbol singly and together.
