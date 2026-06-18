<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Kconfig

## Purpose
Adds the Kconfig entry for the Qualcomm Iris V4L2 stateless video decoder driver.

## Important APIs, Types, And Functions
- Defines `config VIDEO_QCOM_IRIS` as a tristate option named "Qualcomm Iris V4L2 decoder driver".
- Depends on `VIDEO_DEV` and either `ARCH_QCOM` or `COMPILE_TEST`.
- Selects `V4L2_MEM2MEM_DEV`, `QCOM_MDT_LOADER`, `QCOM_SCM`, and `VIDEOBUF2_DMA_CONTIG`.

## Control Flow
Kconfig evaluation exposes the option only when dependencies are met. Selecting it as built-in or module controls whether the Iris objects listed in the Makefile are linked into the kernel or module.

## State And Persistence
No runtime state. The selected value persists only in kernel configuration files such as `.config`.

## Dependencies And Integration Points
Integrates the Iris decoder with the media platform driver menu and ensures required V4L2 mem2mem, VB2 DMA-contiguous, Qualcomm MDT firmware loading, and SCM interfaces are available.

## Risks And Edge Cases
Dependency omissions can allow invalid builds; overly strict dependencies can hide compile-test coverage. Selecting DMA-contiguous constrains expected memory allocation behavior for the driver.

## Test Signals
Kernel `olddefconfig`/menuconfig visibility, `allyesconfig`/`allmodconfig`, module builds, and compile-test builds on non-Qualcomm architectures are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Kconfig -->
