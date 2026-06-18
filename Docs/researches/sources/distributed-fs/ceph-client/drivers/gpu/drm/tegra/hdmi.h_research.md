# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.h

Purpose: defines Tegra HDMI/SOR register offsets and bitfield macros used by `hdmi.c`.

Important APIs/types: macros cover SOR state/power/PLL/lane drive, HDMI generic/audio/AVI/vendor infoframes, ACR/N/CTS audio registers, input control, pin drive/pre-emphasis/peak-current tables, HDA scratch/ELD/presence registers, interrupts, and pad control.

Control flow and state: no executable logic; the file is the hardware ABI for HDMI register programming and debugfs register enumeration.

Dependencies/integration: consumed by `hdmi.c` TMDS tables, encoder enable/disable, IRQ handling, audio setup, and debugfs.

Risks: dense bitfield definitions are easy to misuse because many fields have SoC-specific encodings. HDCP registers are defined although the implementation notes HDCP is not implemented.

Test signals: register trace comparisons during mode-set/audio enable, build coverage, and hardware validation across Tegra20/30/114/124.
