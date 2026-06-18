# sources/cloud-native/containerd/defaults/defaults_unix.go

## Purpose
This Unix build-tagged file defines shared filesystem defaults for Unix-like systems.

## Important APIs, Types, and Functions
`DefaultConfigDir`, `DefaultRootDir`, and `DefaultConfigIncludePattern` point to `/etc/containerd`, `/var/lib/containerd`, and `/etc/containerd/conf.d/*.toml`.

## Control Flow
No executable flow.

## State and Persistence
`DefaultRootDir` is the persistent data root; config paths define daemon configuration discovery.

## Dependencies and Integration Points
Composes with Linux, Darwin, FreeBSD, and other Unix defaults.

## Risks
Path changes affect package layouts, daemon startup, and upgrade compatibility.

## Test Signals
Build and integration tests rely on these defaults unless explicit test roots are passed.
