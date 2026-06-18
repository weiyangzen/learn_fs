# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_msm.c

Purpose: implements Qualcomm MSM ChipIdea glue, including clocks, reset controller support for PHY POR reset, optional PHY muxing, HSIC detection, and controller reset notifications.

Important APIs/types/functions: defines `struct ci_hdrc_msm`, reset op `ci_hdrc_msm_por_reset`, notification callback `ci_hdrc_msm_notify_event`, PHY mux helper `ci_hdrc_msm_mux_phy`, and platform probe/remove.

Control flow: probe allocates glue state, fills platform data with shared-register, streaming-disable, AHB-burst, and override-phy-control quirks, obtains core/interface/optional FS clocks, maps vendor PHY registers, registers reset controller, pulses core reset, enables clocks, optionally selects secondary PHY through syscon, detects HSIC child PHY, and adds the `ci_hdrc` child. Reset notifications configure PHY mode, unclamp secondary PHY, initialize/power PHY, program AHB and workaround registers, and set session-valid override for extcon/role-switch.

State and persistence: stores child platform device, clocks, platform data, reset-controller device, secondary PHY and HSIC booleans, and vendor base MMIO.

Dependencies and integration: uses common clock, reset, syscon/regmap, OF child parsing, PHY APIs, PM runtime no-callback mode, and ChipIdea platform add/remove.

Risks: direct vendor register writes assume resource 1 mapping and correct PHY selection arguments. PHY init/power is tied to core reset/stop notifications rather than core-managed PHY control. FS clock is disabled after reset pulse and must tolerate optional absence.

Test signals: MSM probe/remove, reset-controller users, HSIC and non-HSIC PHY paths, extcon/role-switch session-valid override, and controller stop notification powering off PHY.
