# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Kconfig

Purpose: declares `VIDEO_IPU3_CIO2`, the Intel IPU3 CIO2 CSI-2 receiver driver option.

Important APIs/types/functions: tristate option depends on `VIDEO_DEV`, `PCI`, `ACPI || COMPILE_TEST`, `X86`, and a permissive `IPU_BRIDGE || !IPU_BRIDGE` expression. It selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `V4L2_FWNODE`, and `VIDEOBUF2_DMA_SG`.

Control flow: controls whether the IPU3 CIO2 PCI capture driver is built.

State and persistence: no runtime state.

Dependencies/integration: pairs with `intel/ipu3/Makefile` and may use IPU bridge support depending on config and platform.

Risks and test signals: dependency expression must permit valid build combinations while ensuring required media APIs. Test with IPU bridge built-in/module/off and IPU3 built-in/module, especially symbol resolution for bridge namespace users.
