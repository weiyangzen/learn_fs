# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_tegra.c

Purpose: implements NVIDIA Tegra ChipIdea glue, handling SoC match data, PHY/clock/reset sequencing, runtime PM, Tegra-specific low-power entry, EHCI tuning, and optional double-reset hub behavior.

Important APIs/types/functions: defines `struct tegra_usb`, `struct tegra_usb_soc_info`, match table entries, `tegra_usb_reset_controller`, `tegra_usb_notify_event`, `tegra_usb_internal_port_reset`, `tegra_ehci_hub_control`, `tegra_usb_enter_lpm`, probe/remove, and runtime PM callbacks.

Control flow: probe obtains SoC info, USB PHY, clock, OPP table, runtime-resumes the parent, resets the controller, initializes PHY before touching controller registers, fills platform data, disables runtime PM for ULPI, and adds the `ci_hdrc` child. Hub-control override performs double port reset when requested. Runtime PM gates the parent clock.

State and persistence: stores platform data, child device, SoC info, PHY, clock, and double-reset flag. EHCI tuning is applied on controller reset notifications.

Dependencies and integration: uses Tegra OPP helper, reset controls, USB PHY, OF match data, EHCI internals, runtime PM, and ChipIdea platform add/remove.

Risks: comments note that touching controller AHB-domain registers while clocks are gated can hang the CPU; this is why LPM delegates to `usb_phy_set_suspend`. Port reset override indexes `(wIndex & 0xff) - 1`, so callers must provide valid hub-control requests.

Test signals: Tegra20/30/114/124 probe, runtime suspend/resume, ULPI runtime-PM disable path, double-reset hub requests, EHCI TX fill tuning, and remove power-off sequencing.
