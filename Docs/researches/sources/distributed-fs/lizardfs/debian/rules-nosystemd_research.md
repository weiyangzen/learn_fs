# sources/distributed-fs/lizardfs/debian/rules-nosystemd

## Purpose
This Debian debhelper rules file builds LizardFS packages for older distributions without systemd integration.

## Important APIs, Types, and Functions
It overrides `dh_auto_configure` to run `./configure --with-doc` and `dh_strip` to emit `lizardfs-dbg`. The `%` target delegates all other commands to `dh $@`.

## Control Flow and State
Unlike `debian/rules`, this file does not override init or systemd steps and does not override `dh_gencontrol`; it is selected by `create-deb-package.sh` for Debian 7 and Ubuntu 12/14.

## Dependencies and Integration Points
It depends on the same `configure` wrapper and debhelper package metadata, but intentionally omits systemd-specific installation behavior.

## Risks and Edge Cases
Documentation is still forced on. Version override support from `debian/rules` is absent here, so package version handling can differ between systemd and non-systemd builds. Older distro toolchains may also interact poorly with modern C++17 flags.

## Test Signals
Successful package builds on selected older distros validate this file. Absence of systemd unit handling is expected.
