# sources/distributed-fs/ceph-client/drivers/media/pci/intel/Makefile

Purpose: defines Kbuild objects and subdirectories for Intel media PCI drivers.

Important APIs/types/functions: builds `ipu-bridge.o` for `CONFIG_IPU_BRIDGE`, always descends into `ipu3/` and `ivsc/`, and descends into `ipu6/` when `CONFIG_VIDEO_INTEL_IPU6` is enabled.

Control flow: build-system only.

State and persistence: no state.

Dependencies/integration: aligns top-level Intel Kconfig options with actual objects and subdirectories.

Risks and test signals: incorrect object/subdir gating breaks symbol availability or builds unnecessary code. Test with modular and built-in combinations of IPU bridge, IPU3, IPU6, and IVSC.
