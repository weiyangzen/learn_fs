## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/Makefile

### Purpose
`ralink/Makefile` connects the Ralink vendor directory to the kernel build by descending into `rt2x00/` when `CONFIG_RT2X00` is enabled.

### Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_RT2X00) += rt2x00/`.

### Control Flow
Kbuild evaluates the config symbol and includes or skips the rt2x00 subdirectory accordingly.

### State, Persistence, And Dependencies
There is no runtime state. It depends on Kbuild and the `CONFIG_RT2X00` symbol defined in rt2x00 Kconfig.

### Integration Points
This is the build bridge between the generic wireless driver Makefile and all Ralink rt2x00 library/driver objects.

### Risks
If `CONFIG_RT2X00` is unset, no Ralink rt2x00 objects build even if lower symbols are somehow selected. The file intentionally has no per-driver granularity.

### Test Signals
Check `make drivers/net/wireless/ralink/` with `CONFIG_RT2X00=y/m/n` and inspect included object directories.
