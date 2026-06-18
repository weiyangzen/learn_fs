# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_host.c

## Purpose

`mtu3_host.c` implements MTU3 host-mode glue. It powers and configures host ports, populates the xHCI child device, handles host suspend/resume port power, and configures SoC-specific wakeup-from-IP-sleep registers.

## Important APIs, Types, and Functions

Public functions are `ssusb_wakeup_of_property_parse()`, `ssusb_wakeup_set()`, `ssusb_host_resume()`, `ssusb_host_suspend()`, `ssusb_host_init()`, and `ssusb_host_exit()`. Internal helpers include `ssusb_wakeup_ip_sleep_set()`, `host_ports_num_get()`, `ssusb_host_enable()`, `ssusb_host_disable()`, `ssusb_host_setup()`, and `ssusb_host_cleanup()`. `enum ssusb_uwk_vers` maps several MediaTek wakeup register layouts.

## Control Flow

Host init reads xHCI port counts, powers on host IP, enables all non-disabled U2/U3 ports in host mode, forces host IDDIG, enables VBUS for DRD port0, then populates child platform devices from the device tree. Suspend powers down U3 and U2 ports and host IP; resume powers them back on, optionally skipping port0 when dual-role is currently device. Wakeup parsing reads `wakeup-source` and `mediatek,syscon-wakeup`, and wakeup enable writes version-specific regmap bits.

## State and Persistence Behavior

Host state lives in `ssusb_mtk`: port counts, disabled-port masks, `is_host`, wakeup enable flag, syscon regmap, wakeup register base/version, and VBUS regulator in the OTG switch. Hardware state is IPPC power/port bits and wakeup syscon bits. No software state persists after remove.

## Dependencies and Integration Points

The file depends on OF platform population, regmap/syscon, PHY/clock/power setup done by `mtu3_plat.c`, xHCI child binding, wake IRQ policy, and dual-role state. It is compiled for host-only and dual-role configurations.

## Risks and Test Signals

Risks include SoC wakeup version mismatches, disabled-port mask handling, failing to disable VBUS only when currently host, child xHCI population failures after host hardware is enabled, and suspend/resume interactions with dual-role port0 ownership. Test signals include host-only probe creating xHCI, multiple U2/U3 port capabilities, disabled port masks, wakeup-source syscon programming for each version, suspend/resume with and without port0 skipped, and remove depopulating xHCI before host cleanup.
