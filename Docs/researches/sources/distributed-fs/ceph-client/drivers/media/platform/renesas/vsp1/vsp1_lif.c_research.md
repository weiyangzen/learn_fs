# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.c

Purpose: implements the LCD Controller Interface entity used by internal DRM display pipelines. It configures LIF output thresholds and enables the LIF block that feeds the display unit.

Important APIs and functions: `vsp1_lif_create()` and `lif_configure_stream()`. Generic entity pad handlers provide format enumeration and setting for ARGB/AYUV.

Control flow: constructor creates an internal two-pad entity with the LIF index and format/dimension limits. During stream configuration, the source pad format is read and generation/model-specific threshold values are selected. The code writes `VI6_LIF_CSBTH`, `VI6_LIF_CTRL`, and on non-zero-LBA variants `VI6_LIF_LBA`.

State and persistence: persistent state is mostly the embedded entity plus index. Threshold programming is recomputed at stream configuration and stored in display-list entries. There are no controls.

Dependencies and integration: depends on display-list writes, entity helpers, VSP1 version/feature flags, and DRM setup in `vsp1_drm.c`, which attaches WPF output to LIF and verifies final format.

Risks and test signals: risks include model-specific threshold mistakes, suspicious `format->code == 0` CFMT check, LIF index register offset errors, and LBA quirk regressions. Test display output on Gen2/Gen3/Gen4/RZ/G2L variants, interlaced/progressive modes, and suspend/resume.
