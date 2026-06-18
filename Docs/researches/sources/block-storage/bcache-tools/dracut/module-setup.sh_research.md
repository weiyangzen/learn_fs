# File Research: sources/block-storage/bcache-tools/dracut/module-setup.sh

This dracut module installs bcache support into initramfs images. `check` includes the module in host-only/mount-needed mode only if `bcache` appears in `host_fs_types`; otherwise it permits inclusion. `installkernel` adds the `bcache` kernel module.

The install step copies udev helpers `probe-bcache` and `bcache-register`, then installs `69-bcache.rules`. It relies on udev in initramfs for auto-registration.
