# sources/distributed-fs/ceph-client/security/apparmor/include/apparmor.h

## Purpose
`apparmor.h` defines global AppArmor mediation class IDs and runtime configuration globals shared across the LSM implementation.

## Important APIs and symbols
It defines `AA_CLASS_*` constants for file, capability, rlimits, domain, mount, ptrace, signal, net/netv9, label, module, namespace, io_uring, dbus, and related policy classes. It declares runtime globals such as `aa_g_audit`, `aa_g_debug`, `aa_g_hash_policy`, `aa_g_export_binary`, `aa_g_lock_policy`, `aa_g_logsyscall`, `aa_g_paranoid_load`, and `aa_g_path_max`. Compression level macros map to zstd only when raw binary export is compiled.

## Control flow and integration
Class constants index policydb start states, audit class names, label mediation bitmasks, and feature reporting. Runtime globals are read across audit, policy load, apparmorfs, hashing, path handling, and debug code.

## State and persistence
The globals represent runtime module/boot parameter state. Class IDs are ABI-like policy encoding constants and must stay consistent with userspace policy compilers and kernel unpacking code.

## Dependencies
It depends on Linux types and, conditionally, zstd macros through included compilation units. The note that class IDs beyond 63 require label mediation changes matters because `aa_label.mediates` is a 64-bit mask.

## Risks
Changing class values or `AA_CLASS_LAST` can break policy compatibility and label mediation checks. Runtime global changes affect security behavior system-wide.

## Test signals
Build and boot with feature combinations; verify policy classes mediate as expected and apparmorfs/audit class names align with constants.
