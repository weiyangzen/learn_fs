# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_reg.h

Purpose: This header is the DP controller register map and bitfield catalog used by MSM DP AUX, controller, panel, audio, PSR, SDP, TPG, DSC, and HDCP code.

Important contents: It defines offsets and masks for AHB/global registers (`REG_DP_HW_VERSION`, reset, PHY, clocks, interrupt status/masks), HPD block registers and interrupt bits, AUX transaction/data/status registers, mainlink control/configuration/training/timing registers, MISC colorimetry/VSC bits, lane mapping, ready/level/TU registers, audio packet/timing/infoframe registers, SDP generic/VSC registers, P0 interface timing and TPG registers, DSC DTO, PHY AUX interrupt registers, and DP HDCP/security offsets.

Control flow and integration: The constants are consumed by `dp_display.c` for IRQ status and snapshots, `dp_panel.c` for timing/VSC/TPG/DSC DTO programming, `dp_ctrl.c` for reset/link training/video enable/PSR, `dp_aux.c` for AUX/HPD programming, and `dp_audio.c` for audio packet setup. Register grouping mirrors the driver’s split MMIO windows: AHB, AUX, link, and P0.

State and persistence: The header has no runtime state, but its offsets define persistent hardware state layout. Because split and legacy MMIO mapping both use these offsets, offset errors have broad hardware impact.

Risks and test signals: Risks include SoC revision mismatches, incorrect bit masks during new hardware support, field overlap, and silent hardware hangs from wrong reset/clock/interrupt bits. Test signals are register snapshot sanity, AUX transactions, HPD IRQ ack/mask behavior, link training, audio playback, VSC SDP updates, TPG output, PSR interrupts, and HDCP register users.
