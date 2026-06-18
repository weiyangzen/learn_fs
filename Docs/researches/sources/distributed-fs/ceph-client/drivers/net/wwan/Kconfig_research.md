# sources/distributed-fs/ceph-client/drivers/net/wwan/Kconfig

## Purpose
Defines Kconfig options for the Linux WWAN core and WWAN device drivers in this tree, including core WWAN support, optional debugfs support, simulation, MHI control/MBIM, Qualcomm BAM-DMUX, RPMSG control, Intel IOSM, and MediaTek T7xx.

## Important APIs, Types, And Functions
Key symbols are `WWAN`, `WWAN_DEBUGFS`, `WWAN_HWSIM`, `MHI_WWAN_CTRL`, `MHI_WWAN_MBIM`, `QCOM_BAM_DMUX`, `RPMSG_WWAN_CTRL`, `IOSM`, and `MTK_T7XX`. `IOSM` depends on `PCI` and selects `NET_DEVLINK` plus `RELAY` when debugfs is enabled. `WWAN` depends on `GNSS || GNSS = n`.

## Control Flow
Kconfig controls which objects in the WWAN Makefiles are built. The `if WWAN` block gates all subordinate driver options on the WWAN core.

## State And Persistence
No runtime state. Configuration choices persist in the kernel build config and determine module availability and selected dependencies.

## Dependencies And Integration Points
Integrates with Linux Kconfig, PCI, MHI bus, RPMSG, DMA/PM/Qualcomm SMEM state, DEBUG_FS, RELAY, NET_DEVLINK, and GNSS symbols.

## Risks
Incorrect dependency/select relationships can create build failures or silently omit required support. `WWAN_DEBUGFS` defaults to yes when available, which affects IOSM/MTK debug trace object inclusion through Makefiles.

## Test Signals
Run allmodconfig/allnoconfig and targeted configs for each WWAN driver. Verify IOSM builds as built-in and module with/without `WWAN_DEBUGFS`, and that selected `NET_DEVLINK` is present.
