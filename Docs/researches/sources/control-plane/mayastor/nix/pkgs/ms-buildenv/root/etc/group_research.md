# sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/group

Purpose: static group database for the Mayastor Nix build environment root filesystem.

Important APIs/types/functions: defines `root`, `wheel`, `tty`, `users`, `nixbld` with builders `nixbld1` through `nixbld30`, and `nogroup`.

Control flow: no executable flow; libc/NSS group lookup reads it.

State/persistence: persistent image configuration for build users and group IDs.

Dependencies/integration: works with the buildenv passwd/shadow files and `nsswitch.conf` to support multi-user Nix builds.

Risks: group IDs and builder membership must match Nix daemon expectations. Missing builder users in passwd would break group membership usefulness.

Test signals: Nix builds in the image should be able to use all configured `nixbld` users.
