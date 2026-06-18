<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.c

## Purpose
`unpriv_helpers.c` decides whether unprivileged BPF verifier tests should be disabled. It considers the kernel `unprivileged_bpf_disabled` sysctl and CPU mitigation status, because some unprivileged tests rely on Spectre mitigations being enabled.

## Important APIs, Types, And Functions
- `open_config()` tries `/boot/config-$(uname -r)` then `/proc/config.gz`.
- `config_contains()` scans compressed kernel config for an exact option line.
- `cmdline_contains()` scans `/proc/cmdline` for a boot parameter.
- `get_mitigations_off()` returns true for `mitigations=off` or missing `CONFIG_CPU_MITIGATIONS=y`.
- `get_unpriv_disabled()` is the exported decision function.

## Control Flow
`get_unpriv_disabled()` first reads `/proc/sys/kernel/unprivileged_bpf_disabled`; if nonzero or unreadable, it disables unpriv tests. If sysctl permits unprivileged BPF, it calls `get_mitigations_off()` and disables unpriv tests if mitigations are off or cannot be determined.

## State And Persistence
No mutable persistent state exists. The helper reads procfs/boot config files and closes them.

## Dependencies And Integration Points
It depends on zlib `gzFile`, `uname`, procfs sysctl/cmdline, kernel config availability, and `unpriv_helpers.h`. `test_verifier.c` uses it to decide unprivileged test execution.

## Risks And Edge Cases
If kernel config is unavailable, the helper conservatively disables unprivileged tests. `cmdline_contains()` uses the token length in `strncmp(c, pat, strlen(c))`, which can match prefixes in a surprising way. Config scanning returns `-1` on EOF without a match, so absence and read errors are both treated as unknown/off.

## Test Signals
Verifier output will print that unprivileged execution cannot run when sysctl disables BPF. Otherwise skipped `/u` cases due to mitigation uncertainty indicate this helper returned disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.c -->
