# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/common.h

## Purpose
`common.h` provides shared inline helpers and constants for Landlock selftests. It centralizes capability setup/drop logic, UNIX file descriptor passing, Landlock ruleset enforcement helpers, helper binary names, and common network service fixture structures.

## Important APIs, Types, And Functions
Important helpers include `_init_caps()`, `disable_caps()`, `drop_caps()`, `_change_cap()`, `set_cap()`, `clear_cap()`, `set_ambient_cap()`, `clear_ambient_cap()`, `recv_fd()`, `send_fd()`, `enforce_ruleset()`, `drop_access_rights()`, and `set_unix_address()`. Shared types include `struct protocol_variant` and `struct service_fixture`. Constants include `TMP_DIR` and helper binary paths `bin_sandbox_and_launch`, `bin_wait_pipe`, and `bin_wait_pipe_sandbox`.

## Control Flow
Capability helpers first lock out root privilege regain with `SECBIT_NOROOT | SECBIT_NOROOT_LOCKED`, clear the current capability set, optionally repopulate a controlled permitted set needed by tests, and apply it with libcap. `set_cap()` and `clear_cap()` toggle effective bits for individual capabilities, while ambient helpers also manage inheritable state and `cap_set_ambient()`. `send_fd()` and `recv_fd()` construct or parse `SCM_RIGHTS` ancillary data on UNIX sockets. `enforce_ruleset()` sets `PR_SET_NO_NEW_PRIVS` then calls `landlock_restrict_self()`. `drop_access_rights()` creates and immediately enforces a ruleset. `set_unix_address()` builds unique abstract UNIX socket names from TID and an index.

## State, Persistence, And Dependencies
The helpers mutate process credentials, securebits, ambient capabilities, `no_new_privs`, and Landlock domain state. File descriptor passing transfers live kernel FDs between processes but writes no files. Dependencies include libcap, Linux securebits, Landlock wrappers, kselftest harness metadata, UNIX sockets, network socket address types, and standard process APIs.

## Integration Points
This header is included by multiple Landlock tests, including `audit_test.c` and `base_test.c`. It bridges kselftest metadata with Linux capabilities and Landlock enforcement, and its helper binary names must match the programs built by the Landlock Makefile.

## Risks
Capability and securebit changes are process-wide and hard to undo, so tests must be isolated by the harness. `_init_caps()` keeps a curated list of capabilities; new tests needing other capabilities must update it. `recv_fd()` assumes a valid control message is present and can report `-EIO` for malformed messages. Abstract UNIX socket names include `sys_gettid()`, so callers depend on wrapper availability and Linux-specific behavior.

## Test Signals
Indirect test signals are successful fixture setup in Landlock tests, expected capability elevation/drop behavior around audit control, successful ruleset enforcement, and correct FD transfer in `base_test.c`. Failures often appear as unexpected `EPERM`, missing audit setup privilege, failed `SCM_RIGHTS` transfer, or Landlock enforcement setup errors.
