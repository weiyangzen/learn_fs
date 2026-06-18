# File Research: sources/cow-pools/bcachefs-tools/Makefile

- Main mixed Rust/C build and install driver.
- Locks `VERSION` once at make startup from git, `.version`, or Cargo metadata to avoid DKMS install races.
- Builds C objects into `libbcachefs.a`, then links the Rust `bcachefs` binary via Cargo.
- Defines debug and DKMS option forwarding through `build.vars`, separating userspace `MAKE_DEBUG` from kernel-module debug flags.
- Sets userspace C flags for kernel-derived code and probes pkg-config libraries including blkid, uuid, urcu, libsodium, zlib, lz4, zstd, udev, keyutils, and libunwind.
- Generates systemd service and initramfs hook templates when dependencies are available.
- Installs binary, manpage, initramfs hook, udev rules, symlink command aliases, bash completions, optional systemd units, and DKMS source tree.
- Provides `dkms-reload` with memory-bounded parallelism, package targets, doc generation, vendored kernel-source refresh, and source tarball creation.
