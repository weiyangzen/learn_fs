# File Research: sources/cow-pools/bcachefs-tools/debian/rules

- Debian packaging makefile using debhelper with DKMS support.
- Enables verbose output, disables LTO, enables hardening, and imports dpkg/rust architecture variables.
- Sets Cargo paths, frozen Cargo args, target triple, pkg-config cross variables, `/usr` prefix, and `/usr/sbin`.
- Prepares vendored Cargo dependencies during clean/configure.
- Overrides tests to no-op and suppresses problematic `dh_clean`/`dh_usrlocal` behavior.
- Runs `dh-cargo-built-using` after install to generate Built-Using metadata.
