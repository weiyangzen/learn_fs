# sources/cloud-native/ostree/ci/gh-install.sh

Purpose: installs CI build dependencies on Debian and Ubuntu runners. It reads `/etc/os-release`, builds an apt package list matching libostree's build/test surface, adds distro-conditional packages, and installs any caller-supplied extra packages.

Important APIs/functions: `ID` and `VERSION_CODENAME` from `/etc/os-release`; `PACKAGES` bash array; positional package arguments; apt commands `apt-get -y update` and `apt-get -y install`. FUSE package selection is influenced by caller-supplied `libfuse-dev` or `libfuse3-dev`.

Control flow: only Debian/Ubuntu are supported. The script defaults to `libfuse3-dev` if no FUSE package was requested, appends common build/test packages, chooses `bsdmainutils` vs `bsdextrautils`, conditionally adds old FUSE 2 packages for older releases, then installs everything plus extras.

State and persistence: mutates the host package database and apt cache. It sets `DEBIAN_FRONTEND=noninteractive` to avoid blocking CI.

Dependencies and integration: aligns CI packages with Debian/Ubuntu packaging metadata and libostree optional features such as GPGME, libsoup3, curl, systemd, gtk-doc, gobject introspection, fsverity, SELinux, and JS installed tests.

Risks and test signals: unsupported distro IDs hard-fail. Risks include stale package names across distro releases, old FUSE availability assumptions, and comments noting TODO packaging sync. Test signals are successful apt resolution and subsequent `gh-build.sh` configure/test coverage.
