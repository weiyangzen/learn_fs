# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/dae_main.c

## Purpose
This file adds Data Analytics Engine support to the HiSilicon ZIP driver for hardware that advertises `QM_SUPPORT_DAE`. It initializes DAE memory, appends DAE algorithm names to the UACCE capability string, controls DAE out-of-order AXI shutdown behavior, and folds DAE RAS/error state into ZIP device recovery.

## Important APIs, Types, And Functions
Public functions declared in `zip.h` include `hisi_dae_set_user_domain()`, `hisi_dae_set_alg()`, `hisi_dae_hw_error_enable()`, `hisi_dae_hw_error_disable()`, `hisi_dae_get_err_result()`, `hisi_dae_dev_is_abnormal()`, `hisi_dae_close_axi_master_ooo()`, and `hisi_dae_open_axi_master_ooo()`. `dae_is_support()` gates every operation on the QM capability bit.

`struct hisi_dae_hw_error` and `dae_hw_error[]` map interrupt bits to log messages. Algorithm exposure differs by hardware generation: v5 and later advertise `hashagg`, `udma`, `hashjoin`, and `gather`; earlier supported DAE devices advertise `hashagg`.

## Control Flow
ZIP PF initialization calls `hisi_dae_set_user_domain()` after ZIP cache/user-domain setup. It starts DAE memory initialization and polls a done register. ZIP QM initialization calls `hisi_dae_set_alg()` after setting ZIP algorithms so UACCE users see DAE operations in the same accelerator device. ZIP error callbacks call DAE enable/disable, status, abnormality, and OOO helpers alongside ZIP equivalents.

## State And Persistence
The file stores no private runtime state. It manipulates DAE MMIO registers and appends to `qm->uacce->algs`. Error state lives in hardware status/mask registers and in the common QM error flow.

## Dependencies And Integration Points
It depends on the HiSilicon QM capability model, UACCE algorithm string storage, MMIO polling, and the ZIP module. It is not separately registered; it is linked into `hisi_zip.o`.

## Risks
Risk centers on capability gating and UACCE string length. `hisi_dae_set_alg()` mutates `qm->uacce->algs` using `strcat()` after checking length, so callers must ensure the string is initialized and bounded by `QM_DEV_ALG_MAX_LEN`. DAE error reset decisions can force whole ZIP device recovery when NFE bits are set.

## Test Signals
Test ZIP probe on hardware with and without `QM_SUPPORT_DAE`, UACCE algorithm string contents for pre-v5 and v5, DAE memory-init timeout handling, DAE CE/NFE logging, combined ZIP/DAE recovery result selection, and OOO close/open register polling.
