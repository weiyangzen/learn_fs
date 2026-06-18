# sources/cloud-native/cri-o/pkg/config/sysctl.go

This file parses and validates default sysctl settings from `RuntimeConfig`. It wraps sysctls in a small `Sysctl` type and enforces that user-configured default sysctls are both syntactically strict and known to be namespaced by the kernel.

Important APIs are `NewSysctl`, `(*Sysctl).Key`, `(*Sysctl).Value`, `(*RuntimeConfig).Sysctls`, and `(*Sysctl).Validate`. `Sysctls` iterates `DefaultSysctls`, skips empty entries for backward compatibility, requires exact `key=value` format with no trimming changes, and returns parsed values. `Validate` maps exact keys and prefixes to `IpcNamespace` or `NetNamespace`, rejects IPC sysctls for host IPC pods, rejects net sysctls for host network pods, and rejects anything outside the allowlist.

State is derived only from config strings; there is no persistence. Dependencies are Go `fmt` and `strings`. Integration points include runtime config validation and pod setup logic that needs safe default sysctls. Risks include allowlist maintenance as kernel namespacing evolves and the strict no-space parser rejecting values an operator may expect to be tolerated. Tests in `sysctl_test.go` cover parse success/failure, empty compatibility entries, whitelist failures, and host namespace restrictions.
