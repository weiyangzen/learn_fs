# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Makefile

Purpose: builds the IPU3 CIO2 object when enabled.

Important APIs/types/functions: `obj-$(CONFIG_VIDEO_IPU3_CIO2) += ipu3-cio2.o`.

Control flow: Kbuild-only.

State and persistence: no state.

Dependencies/integration: tied to `VIDEO_IPU3_CIO2` in the sibling Kconfig.

Risks and test signals: object/config mismatch breaks IPU3 builds. Test module and built-in builds of `CONFIG_VIDEO_IPU3_CIO2`.
