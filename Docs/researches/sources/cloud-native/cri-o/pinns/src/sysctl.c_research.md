# sources/cloud-native/cri-o/pinns/src/sysctl.c

Purpose: applies sysctl key/value settings inside the current namespace context for `pinns`.

Important APIs/types/functions: `configure_sysctls`, internal `separate_sysctl_key_value`, and `write_sysctl_to_file`.

Control flow: `configure_sysctls` iterates configured strings, splits each `key=value` in place, validates non-empty key/value, rewrites dots in keys to slashes, opens `/proc/sys` with `O_DIRECTORY|O_PATH`, opens the specific sysctl with `openat`, and writes the value with EINTR retry.

State and persistence: mutates kernel sysctl state in `/proc/sys` for the namespace where `pinns` runs after unshare. It also mutates the input argument strings by replacing `=` and `.` with NUL and `/`.

Dependencies/integration: called from `pinns.c` after namespace creation; uses cleanup macros and logging helpers from `utils.h`.

Risks: in-place mutation means the original sysctl string cannot be reused after configuration. There is no allowlist; caller must ensure only intended sysctls are passed. Write success does not verify full byte count beyond negative return, so short positive writes are not detected. Path traversal through sysctl keys is mitigated only by opening under `/proc/sys`; slash-containing input can still address nested sysctls.

Test signals: no direct tests; integration should cover malformed key/value, namespace-specific sysctls, permission errors, and absent procfs entries.
