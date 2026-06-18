# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Kconfig

Purpose: Vendor-level Kconfig menu for STMicroelectronics wireless devices.

Important APIs and types: Defines `WLAN_VENDOR_ST` as a boolean menu gate defaulting to `y`. When enabled, it sources `drivers/net/wireless/st/cw1200/Kconfig`.

Control flow: Kconfig selection only affects configuration visibility. Disabling the vendor option hides ST driver questions; it does not directly build code.

State and persistence: The selected Kconfig symbols persist in the kernel `.config`.

Dependencies and integration: Integrated from the parent wireless vendor Kconfig tree. Its only child in this subset is the CW1200 family.

Risks: If `WLAN_VENDOR_ST=n`, users cannot select CW1200 bus support even when hardware is present. The file is intentionally minimal and depends on the parent tree for menu placement.

Test signals: `make menuconfig` should show the vendor menu and reveal CW1200 options when enabled. Kconfig lint/build tests should verify the sourced path remains valid.
