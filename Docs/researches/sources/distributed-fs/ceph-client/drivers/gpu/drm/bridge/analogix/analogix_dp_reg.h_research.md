# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.h

Purpose: Register-offset and bitfield header for the MMIO Analogix DP controller.

Important APIs/types/functions: It exports no functions. It defines offsets for reset, function enable, video control, PLL/PHY/power, infoframe/PSR SDP, lane map, analog tuning, interrupt status/masks, system control, packet send, link training, AUX, M/N video, SOC general control, and CRC registers. It also defines masks and encoders for color format, lane mapping, AUX command/status, HPD/stream status, scrambling/training patterns, analog power blocks, and PSR CRC.

Control flow: Used by `analogix_dp_reg.c` to implement all hardware register operations. The macros encode how the core transitions between reset, powered AUX, link training, video slave mode, HPD interrupt handling, AUX transactions, and PSR packet send.

State and persistence: The header describes hardware state only. Register values persist in the controller while powered and are reinitialized by resume/enable paths.

Dependencies and integration: Private to the Analogix DP register implementation. The values must remain aligned with SoC integrations using `analogix_dp_plat_data` and platform `dev_type` checks.

Risks: Many masks are active-low function-enable or active-high power-down bits, making accidental inversion dangerous. Some aliases share bit positions for Rockchip versus generic IP. Mistyped register offsets can cause non-obvious display failures.

Test signals: Build coverage, register write traces during reset/link/video/AUX, Rockchip-specific path validation, and AUX error mapping are the main validation points.
