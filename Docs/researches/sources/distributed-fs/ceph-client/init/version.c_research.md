# sources/distributed-fs/ceph-client/init/version.c

## Purpose
`version.c` provides kernel build identity strings, build notes, and early hostname override support. It wraps final timestamp-sensitive data from `version-timestamp.c`.

## Important APIs, Types, And Functions
- `early_hostname()` handles the `hostname=` early parameter by copying into `init_uts_ns.name.nodename` with truncation warning.
- `linux_proc_banner` defines `/proc/version`-style formatting.
- `BUILD_SALT` and `BUILD_LTO_INFO` emit build metadata notes.
- Weak `init_uts_ns` and `linux_banner` definitions allow a late build step to replace them; including `version-timestamp.c` supplies strong final definitions.
- `EXPORT_SYMBOL_GPL(init_uts_ns)` exposes the initial UTS namespace to GPL code.

## Control Flow
The only executable path is early parameter parsing for hostname. Static data provides banners and namespace defaults.

## State And Persistence
`init_uts_ns` persists globally. `hostname=` can mutate the initial nodename during early boot before normal userspace hostname tools run.

## Dependencies And Integration Points
It depends on generated compile metadata, printk, UTS namespace structures, proc namespace support, early parameter infrastructure, and build-salt/LTO note macros. `start_kernel()` prints `linux_banner`.

## Risks And Edge Cases
Overlong `hostname=` values are truncated with warning. Build system expectations around weak/strong symbol replacement and banner string layout are fragile.

## Test Signals
Booting with `hostname=` should update the initial nodename. `/proc/version`, boot banner output, and exported `init_uts_ns` consumers should reflect generated compile metadata.
