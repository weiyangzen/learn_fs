# sources/distributed-fs/ceph-client/kernel/ksyms_common.c

## Purpose
`ksyms_common.c` contains common kallsyms visibility policy that is independent of full `CONFIG_KALLSYMS` implementation details.

## Important APIs, Types, And Functions
The exported function is `kallsyms_show_value(const struct cred *cred)`. Internal `kallsyms_for_perf()` permits symbol values when `CONFIG_PERF_EVENTS` is enabled and `sysctl_perf_event_paranoid <= 1`. The policy also consults global `kptr_restrict` and `security_capable(..., CAP_SYSLOG, CAP_OPT_NOAUDIT)`.

## Control Flow
For `kptr_restrict == 0`, perf-friendly settings allow values to normal users; otherwise it falls through to the capability check. For `kptr_restrict == 1`, `CAP_SYSLOG` permits values. All other cases return false.

## State And Persistence
The file owns no persistent state. It reads global sysctl/security state that can change at runtime.

## Dependencies And Integration Points
It integrates with `/proc/kallsyms`, debugfs/proc users such as kprobes reporting, perf event policy, credentials, security modules, and the initial user namespace.

## Risks And Edge Cases
The risk is kernel address disclosure. The fallthrough logic intentionally allows capable users when `kptr_restrict` is 0 or 1, but not stricter modes. Changes to perf paranoia semantics or capability policy affect observability surfaces.

## Test Signals
Test by reading kallsyms-dependent outputs under different `kptr_restrict`, `perf_event_paranoid`, user credential, and `CAP_SYSLOG` combinations.
