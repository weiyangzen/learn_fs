# sources/distributed-fs/ceph-client/arch/x86/boot/install.sh

Purpose: legacy `make install` helper for copying an x86 kernel image and System.map into the install directory and invoking LILO when present.

Important APIs and state: shell arguments are kernel version, image path, map path, and install path. It rotates existing `vmlinuz` and `System.map` to `.old`, writes new files, and calls `/sbin/lilo` or `/etc/lilo/install`.

Control flow: `set -e` aborts on command failures. Existing files are moved, then image is copied via `cat` and map via `cp`; fallback is `sync` plus a warning if LILO is absent.

Dependencies and integration: invoked by kernel install target on systems using this script. Depends on shell utilities and optional LILO.

Risks and test signals: paths are unquoted, so install paths with spaces are unsafe. Rotation overwrites previous `.old` backups. Test with temporary install roots, missing LILO, and existing/new file replacement behavior.
