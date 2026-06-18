# File Research: sources/block-storage/bcache-tools/initramfs/hook

This initramfs-tools hook declares `udev` as a prerequisite, copies either `/etc/udev/rules.d/69-bcache.rules` or `/lib/udev/rules.d/69-bcache.rules` into the image, copies the three udev helpers, and adds the `bcache` kernel module manually.

It provides Debian/Ubuntu-style early boot bcache device discovery and registration.
