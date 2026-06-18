# sources/cloud-native/containerd/internal/cri/config/config_unix.go

## Purpose

`config_unix.go` defines non-Windows default CRI image and runtime configuration.

## Important APIs, Types, and Functions

- `defaultNetworkPluginBinDirs` returns `/opt/cni/bin`.
- `DefaultImageConfig` sets default snapshotter, disables snapshot annotations by default, configures pause image, key model, pull timeout, max downloads, and stats period.
- `DefaultRuntimeConfig` builds default runc v2 TOML options and returns default CNI, runtime, security, CDI, unprivileged, and logging settings.

## Control Flow

The runtime default function unmarshals a TOML string into an options map and embeds it into the default `runc` runtime entry.

## State and Persistence Behavior

The file returns in-memory defaults; persistent config writing/loading happens elsewhere.

## Dependencies and Integration Points

It depends on containerd defaults, TOML parsing, runc v2 runtime type strings, and shared config structs in `config.go`.

## Risks and Edge Cases

Defaults are compatibility-sensitive. Notably Unix defaults enable unprivileged ports/ICMP, CDI, and disable hugetlb by default, so changes affect node behavior broadly.

## Test Signals

`config_test.go` and kernel validation tests indirectly cover these defaults.
