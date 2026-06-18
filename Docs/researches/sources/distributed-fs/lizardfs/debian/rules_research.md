# sources/distributed-fs/lizardfs/debian/rules

## Purpose
This Debian debhelper rules file builds LizardFS packages with documentation and systemd/init integration.

## Important APIs, Types, and Functions
It overrides `dh_auto_configure`, `dh_gencontrol`, `dh_strip`, `dh_installinit`, and `dh_installsystemd`. The default `%` target delegates to `dh $@`.

## Control Flow and State
Configure runs `./configure --with-doc`, which delegates to CMake. `dh_gencontrol` passes an optional `-v$(version)` when the environment variable is set by package scripts. Strip output goes to `lizardfs-dbg`. Init and systemd install steps use `--no-start`, and systemd also uses `--no-enable`; both handle the `lizardfs-uraft` package with service name `lizardfs-ha-master`.

## Dependencies and Integration Points
It integrates with `configure`, Debian debhelper, package metadata, service files copied by `create-deb-package.sh`, and the `version` environment variable.

## Risks and Edge Cases
Documentation is always requested. Service behavior intentionally avoids starting/enabling daemons during install. The uraft service naming must match package/service files. Build behavior inherits the `configure` script's limitation that `--without-uraft` is ineffective.

## Test Signals
Debian package build logs from debhelper are the signal. Generated control version, debug package, init scripts, and systemd units should reflect these overrides.
