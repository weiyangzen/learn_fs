# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit.h

## Purpose
`audit.h` is an inline helper implementation for Landlock audit selftests. It owns the raw netlink audit client, audit rule setup/removal, regex-based record matching, stale-record draining, and convenience matchers for Landlock domain allocation and deallocation records.

## Important APIs, Types, And Functions
The main types are `struct audit_filter`, which describes an audit filter rule keyed by record type and executable path, `struct audit_message`, which wraps a netlink header and several audit payload layouts, and `struct audit_records`, which counts access and domain records. Core helpers include `audit_send()`, `audit_recv()`, `audit_request()`, `audit_filter_exe()`, `audit_filter_drop()`, `audit_set_status()`, `regex_escape()`, `audit_match_record()`, `matches_log_domain_allocated()`, `matches_log_domain_deallocated()`, `audit_count_records()`, `audit_init()`, `audit_init_filter_exe()`, `audit_cleanup()`, and `audit_init_with_exe_filter()`.

## Control Flow
Audit setup starts with `audit_init()`, which opens `NETLINK_AUDIT`, enables audit, sets the audit PID to the test process, installs a short receive timeout, and drains stale messages from the backlog. `audit_init_with_exe_filter()` adds an exclude filter for all executables except the current test binary. Test code can also add `audit_filter_drop()` so only Landlock domain-drop records are allowed through. Matching flows through `audit_match_record()`: it compiles a regex, receives records until the type and content match, skips irrelevant records, records the last same-type mismatch for diagnostics, and optionally extracts the domain ID captured by `REGEX_LANDLOCK_PREFIX`. Deallocation matching temporarily extends the socket timeout when a specific domain ID is expected because domain release is asynchronous.

## State, Persistence, And Dependencies
The helpers mutate global kernel audit state for the active audit socket: enabled status, audit PID, and exclude rules. All state is process lifetime scoped but globally visible enough to conflict with a running audit daemon. Filtering stores executable paths without trailing NUL bytes. The file depends on Linux audit UAPI headers, netlink sockets, POSIX regex, socket timeouts, and kselftest logging macros.

## Integration Points
`audit_test.c` includes this header directly and uses its static functions inside kselftest fixtures. The helpers target Landlock-specific audit records `AUDIT_LANDLOCK_ACCESS` and `AUDIT_LANDLOCK_DOMAIN`, matching message formats emitted by the kernel. `common.h` supplies capability manipulation so tests can briefly gain `CAP_AUDIT_CONTROL` before calling these helpers.

## Risks
The helpers require exclusive audit socket ownership; `audit_init()` can fail with `-EEXIST` if auditd or another test owns the socket. Regexes are tightly coupled to audit message formatting, including field order and escaping. Domain deallocation records are asynchronous, so tests must avoid naïve zero-count assertions without a preceding scan. `audit_filter_exe()` currently supports only `AUDIT_EXE`; using other record types returns `-EINVAL`. Because the helpers alter audit rules, cleanup must run with sufficient capability to avoid contaminating subsequent tests.

## Test Signals
Good signals are successful audit initialization, correct matching of Landlock access/domain records, empty `audit_count_records()` after expected messages are consumed, and cleanup that removes both executable and drop filters. Failures identify audit daemon conflicts, netlink protocol errors, regex drift, timeout races, or missing kernel audit/Landlock support.
