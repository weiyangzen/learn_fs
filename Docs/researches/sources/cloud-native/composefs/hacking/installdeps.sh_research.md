# sources/cloud-native/composefs/hacking/installdeps.sh

Purpose: distro-aware dependency installer for composefs development and CI builds.

Important APIs/types/functions: Fedora/RHEL path using dnf, CRB enablement for RHEL-like systems, `dnf builddep composefs`; Debian path with `DEBIAN_FRONTEND=noninteractive`, package list, and `ALLOW_MISSING` split into required vs optional packages.

Control flow: if `/usr/bin/dnf` exists, installs dnf-utils/tar/git/meson and builddeps then exits. Otherwise installs required apt packages and optionally attempts ignored-missing packages.

State/persistence: mutates host/container package database.

Dependencies/integration: CI workflows call it with sudo; build containers rely on it for Meson/C dependencies.

Risks/test signals: package names and `dnf builddep composefs` depend on distro repos. Optional package handling supports old Ubuntu Focal missing `libfsverity-dev`.
