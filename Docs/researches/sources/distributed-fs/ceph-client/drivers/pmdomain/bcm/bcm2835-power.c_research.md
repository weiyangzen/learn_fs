# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm2835-power.c

Purpose: direct PM-register power-domain and reset-controller driver for Broadcom BCM2835-family multimedia/display domains, with ASB bridge handling and BCM2711/RPiVid differences.

Important APIs/types/functions: `struct bcm2835_power` owns PM, ASB, RPiVid ASB bases, onecell data, domain array, and reset controller. `struct bcm2835_power_domain` wraps genpd with domain ID and optional clock. Core helpers include `bcm2835_power_power_on/off()` for PM_GRAFX/IMAGE gates, `bcm2835_asb_control()`, `bcm2835_asb_power_on/off()`, `bcm2835_power_pd_power_on/off()`, `bcm2835_init_power_domain()`, reset ops `bcm2835_reset_reset()` and `bcm2835_reset_status()`, and `bcm2835_power_probe()`.

Control flow: probe obtains PM register bases from the parent `bcm2835_pm` MFD, validates ASB bridge IDs, allocates onecell data, initializes all named domains as initially off, adds parent-child dependencies such as image to H264/ISP/USB/CAM and grafx to V3D, registers reset controller, and registers provider on the parent OF node. Power-on dispatch handles raw PM gates with inrush ramp and memory repair, ASB-backed subdomains with clock/reset/bridge sequencing, and simple LDO/control domains for USB, DSI, CCP2TX, and HDMI. Power-off reverses each path. Reset ops power-cycle V3D/H264/ISP subdomains and report reset-line status bits.

State and persistence: software keeps genpd status, optional clocks, domain hierarchy, and reset controller state. Hardware state persists in PM password-protected registers, ASB bridge stop/ack bits, reset bits, LDO controls, and clock framework state. The driver treats domains as off at boot for Linux reference-count ownership even if firmware left hardware on.

Dependencies/integration: depends on BCM2835 PM MFD parent data, generic PM domains, reset-controller framework, optional clocks named by domain, DT binding indices, MMIO polling, and platform consumers for V3D, H264, ISP, USB, camera, DSI, CCP2TX, and HDMI.

Risks: direct PM access must not be used for domains owned by Raspberry Pi firmware. The inrush loop and memory-repair polling are timing-sensitive. ASB enable/disable ordering is critical to avoid AXI hangs. BCM2711/RPiVid paths intentionally skip legacy power gates. Some named domains such as CAM0/CAM1 exist in the xlate table but lack explicit switch cases, so consumers must match implemented domains or receive `-EINVAL`.

Test signals: ASB ID validation succeeds, all provider indices resolve, V3D/H264/ISP resets power-cycle correctly, USB/HDMI/DSI/CCP2TX register sequences enable hardware, parent-child genpd dependencies hold, memory repair reaches `PM_MRDONE`, and Raspberry Pi firmware-owned systems use `raspberrypi-power` instead when required.
