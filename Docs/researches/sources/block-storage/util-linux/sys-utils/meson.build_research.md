# File Research: sources/block-storage/util-linux/sys-utils/meson.build

This Meson fragment declares source lists and manpage inputs for many `sys-utils` programs in util-linux. The files in this research group are represented by target variables such as `rfkill_sources`, `renice_sources`, `setpgid_sources`, `setsid_sources`, `readprofile_sources`, `rtcwake_sources`, `setarch_sources`, `prlimit_sources`, `lsns_sources`, `mount_sources`, `mountpoint_sources`, `pivot_root_sources`, `nsenter_sources`, `setpriv_sources`, and `swapoff_sources`.

Most entries are simple `files('name.c')` declarations paired with `*_manadocs`. Some targets append shared helper source sets, for example `nsenter_sources` includes `caputils_c` and `exec_shell_c`, `setpriv_sources` includes `caputils_c`, and `swapoff_sources` includes `swapon-common.c`, `swapon-common.h`, and `swapprober_c`. `setpriv-landlock.c` is conditionally added only on Linux builds with `HAVE_LINUX_LANDLOCK_H`.

The file also shows sys-utils build conventions: generated parser sources for `hwclock`, conditional systemd unit installation for `fstrim`, and target-local source variables that later build rules consume.
