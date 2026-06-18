## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Kconfig

### Purpose
`ralink/Kconfig` adds the top-level wireless vendor menu entry for Ralink devices and includes the rt2x00 family configuration.

### Important APIs, Types, And Functions
It defines `config WLAN_VENDOR_RALINK` as a bool defaulting to `y`, wraps subordinate options in `if WLAN_VENDOR_RALINK`, and sources `drivers/net/wireless/ralink/rt2x00/Kconfig`.

### Control Flow
During kernel configuration, disabling the vendor option hides all Ralink driver prompts. Enabling it makes the rt2x00 menu and driver options available.

### State, Persistence, And Dependencies
Configuration state is persisted in the kernel `.config`. This file depends on Kconfig menu processing and the sourced rt2x00 file.

### Integration Points
It is reached from the wireless drivers Kconfig tree and gates all Ralink build options under `drivers/net/wireless/ralink/`.

### Risks
The vendor option does not directly build code; confusion can arise if users expect it to enable a driver by itself. A wrong source path would hide all rt2x00 options.

### Test Signals
Run `make menuconfig` or `scripts/kconfig/conf` with the vendor option both enabled and disabled, and verify rt2x00 symbols appear only in the enabled case.
