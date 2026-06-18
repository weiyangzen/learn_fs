# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Makefile

Purpose: builds the STMicroelectronics STI DRM driver as a composite object.

Important APIs/types/functions: `sti-drm-y` includes mixer, GDP, VID, cursor, compositor, CRTC, plane, HDMI, HDMI PHY, DVO, AWG utilities, VTG, HDA, TV out, HQVDP, and driver glue. `obj-$(CONFIG_DRM_STI) = sti-drm.o`.

Control flow: Kbuild links all listed STI display components into one module or built-in object.

State and persistence: no runtime state.

Dependencies and integration: must match source filenames and internal symbol references across the STI display stack.

Risks: the assignment uses `=` rather than `+=`, which is valid here but should not be duplicated elsewhere for the same symbol. Removing `sti_awg_utils.o` would break video timing generator helpers that call it.

Test signals: module link and full STI driver build.
