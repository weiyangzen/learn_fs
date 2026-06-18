# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Kconfig

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Kconfig

Purpose: Defines the `VIDEO_QCOM_CAMSS` tristate option for the Qualcomm V4L2 Camera Subsystem driver.

Important APIs/types/functions: The option depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, and either `ARCH_QCOM && IOMMU_DMA` or `COMPILE_TEST`. It selects media-controller, V4L2 subdev API, `VIDEOBUF2_DMA_SG`, and `V4L2_FWNODE`.

Control flow/state: No runtime state; it controls whether the `qcom-camss` aggregate object is built and ensures framework dependencies are selected.

Dependencies/integration: Paired with `camss/Makefile`, which builds many CSID/CSIPHY/VFE/video objects into `qcom-camss.o`.

Risks/test signals: Dependency mistakes can either hide CAMSS on valid Qualcomm platforms or allow invalid builds without DMA/IOMMU support. Test compile with ARCH_QCOM, COMPILE_TEST, module and built-in configurations.
