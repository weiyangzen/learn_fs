# subset-b-009860 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbtar -->
# sources/user-network-fs/samba/source3/script/smbtar

## Purpose
Provides the legacy `smbtar` command-line wrapper that turns backup/restore options into an `smbclient` tar-mode invocation against a remote SMB share.

## Important APIs, Types, and Functions
Important routines are `Usage (line 43)`. Key harness variables include `SMBCLIENT (line 19)`, `SMBCLIENT (line 22)`.

## Control Flow
The file is 181 lines and starts with `#!/bin/sh`. Execution begins with command-line parsing/default setup and then performs the requested helper action directly. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `tar`. It is integrated as a source3 utility/helper script rather than a standalone daemon; callers depend on its command-line contract and process exit status.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. The final command uses shell `eval` around user-derived options, so quoting behavior is part of the compatibility surface and must be treated carefully.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of smbclient, tar paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbtar -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/strip_trail_ws.pl -->
# sources/user-network-fs/samba/source3/script/strip_trail_ws.pl

## Purpose
Filters a file in place, removing trailing spaces and tabs from each line while preserving the original content order.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 18 lines and starts with `#!/usr/bin/perl -w`. Execution begins with command-line parsing/default setup and then performs the requested helper action directly. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
It is integrated as a source3 utility/helper script rather than a standalone daemon; callers depend on its command-line contract and process exit status.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/strip_trail_ws.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/dlopen.sh -->
# sources/user-network-fs/samba/source3/script/tests/dlopen.sh

## Purpose
Builds a temporary C helper and uses `dlopen(RTLD_NOW)` to prove that supplied Samba modules can be dynamically loaded with the given compiler/linker flags.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 90 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `rm`, `dlopen`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of rm, dlopen paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/dlopen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/fake_snap.pl -->
# sources/user-network-fs/samba/source3/script/tests/fake_snap.pl

## Purpose
Implements a small snapshot command shim for tests, creating and deleting timestamped snapshot directories through a controlled, untainted path flow.

## Important APIs, Types, and Functions
Important routines are `_untaint_path (line 8)`, `_create_snapshot (line 18)`, `_delete_snapshot (line 42)`.

## Control Flow
The file is 85 lines and starts with `#!/usr/bin/perl -w`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `mkdir`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of mkdir paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/fake_snap.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/full_audit_segfault/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/full_audit_segfault/run.sh

## Purpose
Runs a `vfstest` command file under a TALLOC free-fill setting to exercise the full_audit VFS regression path that previously segfaulted.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: run.sh VFSTEST`. Key harness variables include `TALLOC_FILL_FREE (line 9)`, `TESTBASE (line 12)`, `VFSTEST (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 25 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 22: testit "vfstest" "$VFSTEST" -f "$TESTBASE/vfstest.cmd" "$ADDARGS" ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `vfstest`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of vfstest paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/full_audit_segfault/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/getset_quota.py -->
# sources/user-network-fs/samba/source3/script/tests/getset_quota.py

## Purpose
Acts as the fake quota backend for tests, loading quota records from a text database and serving get/set operations in the format expected by Samba quota helpers.

## Important APIs, Types, and Functions
Important routines are `__init__ (line 32)`, `quota_to_str (line 44)`, `quota_to_db_str (line 48)`, `load_quotas (line 52)`, `set_quotas (line 77)`, `get_quotas (line 90)`, `main (line 97)`, `main (line 154)`. Important Python types are `Quota (line 31)`.

## Control Flow
The file is 154 lines and starts with `#!/usr/bin/env python3`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
State touched or modeled by this file includes fake quota database/configuration.

## Dependencies and Integration Points
External command integrations: `smbcquotas`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes fake quota database/configuration, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of smbcquotas paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/getset_quota.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/printing/modprinter.pl -->
# sources/user-network-fs/samba/source3/script/tests/printing/modprinter.pl

## Purpose
Provides the scripted printer add/delete helper used by printing tests, editing `smb.conf` sections for printer shares.

## Important APIs, Types, and Functions
Important routines are `usage (line 20)`.

## Control Flow
The file is 144 lines and starts with `#!/usr/bin/perl -w`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
State touched or modeled by this file includes server configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `cp`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes server configuration, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of cp paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/printing/modprinter.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/printing/printing_var_exp_lpr_cmd.sh -->
# sources/user-network-fs/samba/source3/script/tests/printing/printing_var_exp_lpr_cmd.sh

## Purpose
Captures print-command argument expansion into a selftest log so printing variable substitution can be asserted.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 9 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `rm`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/printing/printing_var_exp_lpr_cmd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/smbspool_argv_wrapper.c -->
# sources/user-network-fs/samba/source3/script/tests/smbspool_argv_wrapper.c

## Purpose
Wraps `smbspool` so tests can emulate CUPS setting the device URI in `argv[0]` before executing the backend.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 72 lines and starts with `/*`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbspool`, `execve`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of smbspool, execve paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/smbspool_argv_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/stream-depot/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/stream-depot/run.sh

## Purpose
Runs the stream-depot VFS `vfstest` scenario in a temporary directory to validate named-stream storage behavior.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: run.sh VFSTEST PREFIX`. Key harness variables include `TESTBASE (line 9)`, `VFSTEST (line 10)`, `PREFIX (line 11)`, `ADDARGS (line 13)`, `VFSTEST_PREFIX (line 15)`, `VFSTEST_TMPDIR (line 16)`, `NUM (line 28)`.

## Control Flow
The file is 36 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 25: testit "vfstest" $VFSTEST -f $TESTBASE/vfstest.cmd $ADDARGS || failed=$(expr $failed + 1)`, `line 27: subunit_start_test $testname`, `line 30: echo "streams_depot left ${NUM} in .streams, expected 3" | subunit_fail_test $testname`, `line 33: subunit_pass_test $testname`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `vfstest`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of vfstest paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/stream-depot/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_acl_xattr.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_acl_xattr.sh

## Purpose
Blackbox/selftest shell script for Samba's acl xattr behavior. It drives the local test environment through `smbclient`, `smbcacls`, `rm`, `touch`, `grep`, `awk`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS`. Important routines are `setup_remote_file (line 26)`, `smbcacls_x (line 37)`, `nt_affects_posix (line 54)`, `nt_affects_chown (line 75)`, `nt_affects_chgrp (line 110)`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `SMBCACLS (line 17)`, `ADDARGS (line 19)`, `SMBCLIENT (line 20)`, `SMBCACLS (line 21)`.

## Control Flow
The file is 156 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 144: testit "setup remote file tmp" setup_remote_file tmp`, `line 145: testit "setup remote file ign_sysacls" setup_remote_file ign_sysacls`, `line 146: testit "smbcacls -x" smbcacls_x tmp`, `line 147: testit "nt_affects_posix tmp" nt_affects_posix tmp "true"`, `line 148: testit "nt_affects_posix ign_sysacls" nt_affects_posix ign_sysacls "false"`, `line 149: testit "setup remote file tmp" setup_remote_file tmp`, `line 150: testit "setup remote file ign_sysacls" setup_remote_file ign_sysacls`, `line 151: testit "nt_affects_chown tmp" nt_affects_chown tmp`, `line 152: testit "nt_affects_chown ign_sysacls" nt_affects_chown ign_sysacls`, `line 153: testit "setup remote file tmp" setup_remote_file tmp`; plus 3 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcacls`, `rm`, `touch`, `grep`, `awk`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcacls, rm, touch, grep, awk, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_acl_xattr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_outstanding.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_aio_outstanding.sh

## Purpose
Blackbox/selftest shell script for Samba's aio outstanding behavior. It drives the local test environment through `smbclient`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_aio_outstanding.sh \`. Key harness variables include `CONF (line 16)`, `SMBCLIENT (line 17)`, `SERVER (line 18)`, `SHARE (line 19)`, `SAMBA_DEPRECATED_SUPPRESS (line 22)`, `CLI_FORCE_INTERACTIVE (line 45)`, `CLIENT_PID (line 50)`.

## Control Flow
The file is 99 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 96: testit "check_panic" test $panic_count_0 -eq $panic_count_1 ||`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_outstanding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_ratelimit.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_aio_ratelimit.sh

## Purpose
Blackbox/selftest shell script for Samba's aio ratelimit behavior. It drives the local test environment through `smbclient`, `sleep`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: "${SELF}" SERVERCONFFILE SMBCLIENT \`. Important routines are `test_aio_ratelimit_basic (line 32)`, `test_aio_ratelimit_burst (line 88)`, `test_aio_ratelimit_recovery (line 138)`. Key harness variables include `SELF (line 5)`, `CONF (line 13)`, `SMBCLIENT (line 14)`, `SERVER (line 15)`, `LOCAL_PATH (line 16)`, `SHARE (line 17)`, `SAMBA_DEPRECATED_SUPPRESS (line 20)`, `SECONDS (line 43)`, `CLI_FORCE_INTERACTIVE (line 46)`, `CLI_FORCE_INTERACTIVE (line 57)`; plus 10 more.

## Control Flow
The file is 208 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 196: testit "test_aio_ratelimit_basic" \`, `line 200: testit "test_aio_ratelimit_burst" \`, `line 204: testit "test_aio_ratelimit_recovery" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `sleep`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, sleep, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_ratelimit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_async_req.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_async_req.sh

## Purpose
Blackbox/selftest shell script for Samba's async req behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Key harness variables include `SOCKET_WRAPPER_IPV4_NETWORK (line 8)`.

## Control Flow
The file is 14 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 11: testit "async_connect_send" $VALGRIND $BINDIR/async_connect_send_test ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_async_req.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bad_auditnames.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_bad_auditnames.sh

## Purpose
Blackbox/selftest shell script for Samba's bad auditnames behavior. It drives the local test environment through `smbclient`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SHARE USERNAME PASSWORD SMBCLIENT`. Important routines are `can_connect (line 24)`. Key harness variables include `SERVER (line 14)`, `SHARE (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `SMBCLIENT (line 18)`, `SMBCLIENT (line 19)`.

## Control Flow
The file is 29 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 29: testit "Cannot connect to share $SHARE" can_connect || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `grep`. Sourced/helper scripts include `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bad_auditnames.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bug15435_widelink_dfs.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_bug15435_widelink_dfs.sh

## Purpose
Blackbox/selftest shell script for Samba's bug15435 widelink dfs behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_bug15435_widelink_dfs.sh SERVER SERVER_IP USERNAME PASSWORD SMBCLIENT CONFIGURATION <smbclient arguments>`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `CONFIGURATION (line 17)`, `ADDARGS (line 19)`.

## Control Flow
The file is 28 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient "smbclient as $DOMAIN\\$USERNAME" 'ls' "//$SERVER/msdfs-share-wl" -U$DOMAIN\\$USERNAME%$PASSWORD $ADDARGS -c 'cd msdfs-src1' || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bug15435_widelink_dfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_chdir_cache.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_chdir_cache.sh

## Purpose
Blackbox/selftest shell script for Samba's chdir cache behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_chdir_cache.sh \`. Key harness variables include `CONF (line 16)`, `SMBCLIENT (line 18)`, `SMBCONTROL (line 20)`, `SERVER (line 22)`, `SHARE (line 24)`, `PREFIX (line 26)`, `TESTENV (line 28)`, `SAMBA_DEPRECATED_SUPPRESS (line 32)`, `CLI_FORCE_INTERACTIVE (line 50)`, `CLIENT_PID (line 55)`.

## Control Flow
The file is 120 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 91: testit "reload config 1" \`, `line 108: testit "reload config 2" \`, `line 117: testit "Verify we got at least one chdir error" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_chdir_cache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_close_denied_share.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_close_denied_share.sh

## Purpose
Blackbox/selftest shell script for Samba's close denied share behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `sharesec`, `kill`, `sleep`, `mkfifo`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_close_denied_share.sh \`. Key harness variables include `CONF (line 13)`, `SHARESEC (line 14)`, `SMBCLIENT (line 15)`, `SMBCONTROL (line 16)`, `SERVER (line 17)`, `SHARE (line 18)`, `CLI_FORCE_INTERACTIVE (line 30)`, `CLIENT_PID (line 35)`, `COUNT (line 51)`, `COUNT (line 66)`.

## Control Flow
The file is 78 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 45: testit "smbcontrol" ${SMBCONTROL} ${CONF} smbd close-denied-share ${SHARE} ||`, `line 54: testit "Verify close-denied-share did not kill valid client" \`, `line 57: testit "Deny access" ${SHARESEC} ${CONF} --replace S-1-1-0:DENIED/0x0/FULL \`, `line 60: testit "smbcontrol" ${SMBCONTROL} ${CONF} smbd close-denied-share ${SHARE} ||`, `line 69: testit "Verify close-denied-share did kill now-invalid client" \`, `line 75: testit "Allow access" ${SHARESEC} ${CONF} --replace S-1-1-0:ALLOWED/0x0/FULL \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `sharesec`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, live daemon control messages, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, sharesec, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_close_denied_share.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_deadtime.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_deadtime.sh

## Purpose
Blackbox/selftest shell script for Samba's deadtime behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_deadtime.sh IP`.

## Control Flow
The file is 67 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 60: testit "deadtime" test $? -eq 0 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, live daemon control messages, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_deadtime.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_stream.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_delete_stream.sh

## Purpose
Blackbox/selftest shell script for Samba's delete stream behavior. It drives the local test environment through `smbclient`, `net`, `smbcacls`, `mkdir`, `rm`, `touch`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS NET SHARE"`. Important routines are `setup_testfile (line 30)`, `remove_testfile (line 51)`, `set_win_owner (line 59)`, `delete_stream (line 66)`, `win_owner_is (line 89)`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `PREFIX (line 16)`, `SMBCLIENT (line 17)`, `SMBCACLS (line 18)`, `NET (line 19)`, `SHARE (line 20)`, `SMBCLIENT (line 22)`; plus 2 more.

## Control Flow
The file is 123 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 105: testit "create testfile" setup_testfile $SHARE || exit 1`, `line 108: testit "grant SeRestorePrivilege" $NET rpc rights grant $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || exit 1`, `line 111: testit "give owner with SeRestorePrivilege" set_win_owner "$SERVER\user1" || exit 1`, `line 112: testit "verify owner" win_owner_is "$SERVER/user1" || exit 1`, `line 115: testit "delete stream" delete_stream $SHARE afile || exit 1`, `line 118: testit "remove testfile" remove_testfile $SHARE || exit 1`, `line 121: testit "revoke SeRestorePrivilege" $NET rpc rights revoke $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || exit 1`.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcacls`, `mkdir`, `rm`, `touch`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcacls, mkdir, rm, touch, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_stream.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_veto_files_only_rmdir.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_delete_veto_files_only_rmdir.sh

## Purpose
Blackbox/selftest shell script for Samba's delete veto files only rmdir behavior. It drives the local test environment through `smbclient`, `ln`, `mkdir`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SERVER_IP USERNAME PASSWORD SHAREPATH SMBCLIENT`. Important routines are `test_dangle_symlink_delete_veto_rmdir (line 35)`, `test_dangle_symlink_veto_files_nodelete (line 106)`. Key harness variables include `SERVER (line 14)`, `SERVER_IP (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `SHAREPATH (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 21)`, `ADDARGS (line 22)`.

## Control Flow
The file is 182 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 173: testit "rmdir can delete directory containing dangling symlink" \`, `line 178: testit "rmdir cannot delete directory delete_veto_files_no containing dangling symlink" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `ln`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, ln, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_veto_files_only_rmdir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_command.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_dfree_command.sh

## Purpose
Blackbox/selftest shell script for Samba's dfree command behavior. It drives the local test environment through `smbclient`, `awk`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_dfree_command.sh SERVER DOMAIN USERNAME PASSWORD PREFIX SMBCLIENT`. Important routines are `test_smbclient_dfree (line 28)`. Key harness variables include `SERVER (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `PREFIX (line 18)`.

## Control Flow
The file is 69 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: test_smbclient_dfree()`, `line 37: subunit_start_test "$name"`, `line 43: subunit_pass_test "$name"`, `line 46: echo "$output" | subunit_fail_test "$name"`, `line 50: echo "$output" | subunit_fail_test "$name"`, `line 56: test_smbclient_dfree "Test dfree command share root SMB3" dfree "l" "2000 1024. 20" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=SMB3 || failed=$(expr $failed + 1)`, `line 57: test_smbclient_dfree "Test dfree command subdir1 SMB3" dfree "cd subdir1; l" "8000 1024. 80" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=SMB3 || failed=$(expr $faile`, `line 58: test_smbclient_dfree "Test dfree command subdir2 SMB3" dfree "cd subdir2; l" "32000 1024. 320" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=SMB3 || failed=$(expr $fai`, `line 61: test_smbclient_dfree "Test dfree command share root NT1" dfree "l" "2000 1024. 20" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=NT1 || failed=$(expr $failed + 1)`, `line 63: test_smbclient_dfree "Test dfree command subdir1 NT1" dfree "cd subdir1; l" "2000 1024. 20" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=NT1 || failed=$(expr $failed `; plus 1 more.

## State and Persistence Behavior
State touched or modeled by this file includes fake disk-free configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `awk`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes fake disk-free configuration, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_command.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_quota.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_dfree_quota.sh

## Purpose
Blackbox/selftest shell script for Samba's dfree quota behavior. It drives the local test environment through `smbclient`, `smbcacls`, `smbcquotas`, `kill`, `sleep`, `mkdir`; plus 4 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_dfree_quota.sh SERVER DOMAIN USERNAME PASSWORD LOCAL_PATH SMBCLIENT SMBCQUOTAS SMBCACLS`. Important routines are `sighup_smbd (line 31)`, `conf_lines (line 36)`, `setup_1_conf (line 88)`, `setup_conf (line 97)`, `test_smbclient_dfree (line 112)`, `test_smbclient_dfree_2 (line 144)`, `test_smbcquotas (line 174)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `ENVDIR (line 17)`, `WORKDIR (line 18)`, `CONFFILE (line 26)`.

## Control Flow
The file is 303 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 112: test_smbclient_dfree()`, `line 123: subunit_start_test "$name"`, `line 130: subunit_pass_test "$name"`, `line 133: echo "$output" | subunit_fail_test "$name"`, `line 137: echo "$output" | subunit_fail_test "$name"`, `line 144: test_smbclient_dfree_2()`, `line 152: subunit_start_test "$name"`, `line 162: subunit_pass_test "$name"`, `line 165: echo "$output" | subunit_fail_test "$name"`, `line 169: echo "$output" | subunit_fail_test "$name"`; plus 28 more.

## State and Persistence Behavior
State touched or modeled by this file includes fake quota database/configuration, fake disk-free configuration, running smbd process signaling. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcacls`, `smbcquotas`, `kill`, `sleep`, `mkdir`, `rm`, `touch`, `awk`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes fake quota database/configuration, fake disk-free configuration, running smbd process signaling, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcacls, smbcquotas, kill, sleep, mkdir, rm, touch paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_quota.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dropbox.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_dropbox.sh

## Purpose
Blackbox/selftest shell script for Samba's dropbox behavior. It drives the local test environment through `smbclient`, `chmod`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER DOMAIN USERNAME PASSWORD PREFIX TARGET_ENV SMBCLIENT`. Important routines are `test_dropbox (line 30)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `PREFIX (line 17)`, `TARGET_ENV (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 21)`, `ADDARGS (line 22)`.

## Control Flow
The file is 88 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 84: testit "dropbox dirmode 0733" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `chmod`, `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, chmod, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dropbox.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_durable_handle_reconnect.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_durable_handle_reconnect.sh

## Purpose
Blackbox/selftest shell script for Samba's durable handle reconnect behavior. It drives the local test environment through `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Key harness variables include `SMBD_LOG_FILES (line 22)`, `SMBD_LOG_FILES (line 25)`.

## Control Flow
The file is 54 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 16: testit "durable_v2_delay.durable_v2_reconnect_delay" $VALGRIND \`, `line 28: testit "durable_v2_delay.durable_v2_reconnect_delay_msec" $VALGRIND \`, `line 45: testit "durable-v2-regressions.durable_v2_reconnect_bug15624" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `rm`. Sourced/helper scripts include `. $(dirname $0)/../../../testprogs/blackbox/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_durable_handle_reconnect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_failure.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_failure.sh

## Purpose
Blackbox/selftest shell script for Samba's failure behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `test_failure (line 12)`, `test_success (line 17)`.

## Control Flow
The file is 34 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 22: testit "success" \`, `line 26: testit "failure" \`, `line 30: testit "success" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_failure.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fakedircreatetimes.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_fakedircreatetimes.sh

## Purpose
Blackbox/selftest shell script for Samba's fakedircreatetimes behavior. It drives the local test environment through `smbclient`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_fakedircreatetimes.sh SERVER SERVER_IP USERNAME PASSWORD LOCAL_PATH PREFIX SMBCLIENT ADDARGS`. Important routines are `test_fakedircreatetimes (line 35)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCAL_PATH (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `SMBCLIENT (line 17)`, `ADDARGS (line 19)`, `SAMBA_DEPRECATED_SUPPRESS (line 27)`.

## Control Flow
The file is 65 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 60: testit "fakedircreatetimes" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `grep`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fakedircreatetimes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fifo.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_fifo.sh

## Purpose
Blackbox/selftest shell script for Samba's fifo behavior. It drives the local test environment through `smbclient`, `mkfifo`, `mkdir`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER DOMAIN USERNAME PASSWORD PREFIX TARGET_ENV SMBCLIENT`. Important routines are `test_fifo (line 33)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `PREFIX (line 17)`, `TARGET_ENV (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 21)`, `ADDARGS (line 22)`.

## Control Flow
The file is 83 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 80: testit "list directory containing a fifo" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `mkfifo`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, mkfifo, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fifo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_close_share.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_force_close_share.sh

## Purpose
Blackbox/selftest shell script for Samba's force close share behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `mkdir`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: $0 SERVERCONFFILE SMBCLIENT SMBCONTROL IP aio_delay_inject_sharename PREFIX`. Key harness variables include `CONFIGURATION (line 17)`, `SMBCONTROL (line 19)`, `SERVER (line 20)`, `SHARE (line 21)`, `PREFIX (line 22)`, `SAMBA_DEPRECATED_SUPPRESS (line 26)`, `FIFO_STDIN (line 37)`, `FIFO_STDOUT (line 38)`, `FIFO_STDERR (line 39)`, `TESTFILE (line 40)`; plus 3 more.

## Control Flow
The file is 115 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 89: testit "smbcontrol" ${SMBCONTROL} ${CONFIGURATION} smbd close-share ${SHARE} ||`, `line 105: testit "Verify close-share did cancel the file put" \`, `line 111: test_smbclient "remove_testfile" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, live daemon control messages, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, kill, sleep, mkfifo, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_close_share.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_create_mode.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_force_create_mode.sh

## Purpose
Blackbox/selftest shell script for Samba's force create mode behavior. It drives the local test environment through `smbclient`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER DOMAIN USERNAME PASSWORD PREFIX TARGET_ENV SMBCLIENT`. Important routines are `test_force_create_mode (line 29)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `PREFIX (line 17)`, `TARGET_ENV (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 21)`, `ADDARGS (line 22)`.

## Control Flow
The file is 72 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 68: testit "test_mode=0664" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_create_mode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_group_change.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_force_group_change.sh

## Purpose
Blackbox/selftest shell script for Samba's force group change behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `rm`, `grep`, `sed`, `cp`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_force_group_change.sh SERVER USERNAME PASSWORD LOCAL_PATH SMBCLIENT SMBCONTROL"`. Important routines are `test_force_group_change (line 25)`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `LOCAL_PATH (line 15)`, `SMBCLIENT (line 16)`, `SMBCONTROL (line 17)`, `SERVER_CONFIG (line 32)`, `SERVER_CONFIG_SAVE (line 33)`, `SERVER_CONFIG_NEW (line 34)`.

## Control Flow
The file is 73 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 69: testit "test force group change" \`.

## State and Persistence Behavior
State touched or modeled by this file includes server configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `rm`, `grep`, `sed`, `cp`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes server configuration, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, rm, grep, sed, cp paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_group_change.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_user_unlink.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_force_user_unlink.sh

## Purpose
Blackbox/selftest shell script for Samba's force user unlink behavior. It drives the local test environment through `smbclient`, `mkdir`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `test_forced_user_can_delete (line 15)`.

## Control Flow
The file is 41 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 34: testit "test_forced_user_can_delete" test_forced_user_can_delete || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_user_unlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_forceuser_validusers.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_forceuser_validusers.sh

## Purpose
Blackbox/selftest shell script for Samba's forceuser validusers behavior. It drives the local test environment through `smbclient`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_forceuser_validusers.sh SERVER DOMAIN USERNAME PASSWORD LOCAL_PATH SMBCLIENT <smbclient arguments>`. Important routines are `run_cmd_nooutput (line 29)`, `test_force_user_valid_users (line 47)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `LOCAL_PATH (line 17)`, `SMBCLIENT (line 18)`, `SMBCLIENT (line 19)`, `ADDARGS (line 21)`, `CMD (line 31)`, `SMB_SHARE (line 49)`.

## Control Flow
The file is 60 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 54: testit "force user not works when combined with valid users" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_forceuser_validusers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fruit_resource_stream.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_fruit_resource_stream.sh

## Purpose
Blackbox/selftest shell script for Samba's fruit resource stream behavior. It drives the local test environment through `smbclient`, `rm`, `touch`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SHARE USERNAME PASSWORD LOCAL_PATH SMBCLIENT`. Important routines are `put_then_delete_file (line 27)`. Key harness variables include `SERVER (line 14)`, `SHARE (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `LOCAL_PATH (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 20)`.

## Control Flow
The file is 41 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 36: testit "resource_stream" put_then_delete_file || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`, `touch`. Sourced/helper scripts include `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm, touch paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fruit_resource_stream.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_give_owner.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_give_owner.sh

## Purpose
Blackbox/selftest shell script for Samba's give owner behavior. It drives the local test environment through `smbclient`, `net`, `smbcacls`, `rm`, `touch`, `grep`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS NET SHARE"`. Important routines are `setup_testfile (line 30)`, `remove_testfile (line 40)`, `set_win_owner (line 47)`, `win_owner_is (line 56)`, `add_ace (line 74)`, `chown_give_fails (line 114)`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `PREFIX (line 16)`, `SMBCLIENT (line 17)`, `SMBCACLS (line 18)`, `NET (line 19)`, `SHARE (line 20)`, `SMBCLIENT (line 22)`; plus 2 more.

## Control Flow
The file is 147 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 128: testit "create testfile" setup_testfile $SHARE afile || failed=$(expr $failed + 1)`, `line 129: testit "verify owner" win_owner_is $SHARE afile "$SERVER/$USERNAME" || failed=$(expr $failed + 1)`, `line 132: testit "grant SeRestorePrivilege" $NET rpc rights grant $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 133: testit "grant full rights" add_ace $SHARE afile "ACL:$SERVER\\$USERNAME:ALLOWED/0x0/FULL" || failed=$(expr $failed + 1)`, `line 136: testit "give owner with SeRestorePrivilege" set_win_owner $SHARE afile "$SERVER\user1" || failed=$(expr $failed + 1)`, `line 137: testit "verify owner" win_owner_is $SHARE afile "$SERVER/user1" || failed=$(expr $failed + 1)`, `line 138: testit "take owner" set_win_owner $SHARE afile "$SERVER\\$USERNAME" || failed=$(expr $failed + 1)`, `line 139: testit "verify owner" win_owner_is $SHARE afile "$SERVER/$USERNAME" || failed=$(expr $failed + 1)`, `line 142: testit "revoke SeRestorePrivilege" $NET rpc rights revoke $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 143: testit "give owner without SeRestorePrivilege" chown_give_fails $SHARE afile "$SERVER\user1" NT_STATUS_INVALID_OWNER || failed=$(expr $failed + 1)`; plus 1 more.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcacls`, `rm`, `touch`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcacls, rm, touch, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_give_owner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_groupmap.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_groupmap.sh

## Purpose
Blackbox/selftest shell script for Samba's groupmap behavior. It drives the local test environment through `rm`, `awk`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `testone (line 6)`, `tstart (line 12)`, `treport (line 17)`. Key harness variables include `TBASE (line 14)`, `TNOW (line 19)`, `TBASE (line 21)`, `NLOCAL (line 26)`, `NGROUP (line 27)`, `NBUILTIN (line 28)`, `DOMSID (line 29)`, `FORSID (line 30)`.

## Control Flow
The file is 217 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `rm`, `awk`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of rm, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_groupmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_guest_auth.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_guest_auth.sh

## Purpose
Blackbox/selftest shell script for Samba's guest auth behavior. It drives the local test environment through `smbclient`, `net`, `smbcontrol`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SMBCLIENT SMBCONTROL NET CONFIGURATION`. Important routines are `prepare_empty_builtin_guests (line 27)`, `add_local_guest_to_builtin_guests (line 54)`, `test_smbclient (line 64)`. Key harness variables include `SERVER (line 15)`, `SMBCLIENT (line 16)`, `SMBCONTROL (line 17)`, `NET (line 18)`, `CONFIGURATION (line 19)`, `SIDS (line 25)`, `TMP (line 29)`, `SIDS (line 36)`.

## Control Flow
The file is 106 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 64: test_smbclient()`, `line 74: testit "smbclient_guest_at_startup" \`, `line 75: test_smbclient ||`, `line 90: testit "smbclient_guest_auth_without_members" \`, `line 91: test_smbclient ||`, `line 102: testit "smbclient_works_after_restored_setup" \`, `line 103: test_smbclient ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcontrol`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcontrol paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_guest_auth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_homes.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_homes.sh

## Purpose
Blackbox/selftest shell script for Samba's homes behavior. It drives the local test environment through `smbclient`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_homes.sh SERVER USERNAME PASSWORD LOCAL_PATH PREFIX SMBCLIENT CONFIGURATION"`. Important routines are `test_gooduser_home (line 25)`, `test_eviluser_home (line 58)`, `test_slashuser_home (line 91)`. Key harness variables include `SERVER (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCAL_PATH (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `CONFIGURATION (line 17)`, `USERNAME (line 33)`, `USERNAME (line 66)`, `USERNAME (line 99)`.

## Control Flow
The file is 136 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 124: testit "test gooduser home" \`, `line 128: testit "test eviluser home reject" \`, `line 132: testit "test slashuser home reject" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_homes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_inherit_owner.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_inherit_owner.sh

## Purpose
Blackbox/selftest shell script for Samba's inherit owner behavior. It drives the local test environment through `smbclient`, `net`, `smbcacls`, `chown`, `mkdir`, `rm`; plus 4 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS NET SHARE INH_WIN INH_UNIX <additional args>`. Important routines are `create_file (line 33)`, `create_dir (line 45)`, `cleanup_file (line 56)`, `cleanup_dir (line 65)`, `set_win_owner (line 74)`, `unix_owner_id_is (line 82)`, `get_unix_id (line 95)`, `win_owner_is (line 103)`. Key harness variables include `SERVER (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `PREFIX (line 17)`, `SMBCLIENT (line 18)`, `SMBCACLS (line 19)`, `NET (line 20)`, `SHARE (line 21)`, `INH_WIN (line 22)`, `INH_UNIX (line 23)`; plus 19 more.

## Control Flow
The file is 170 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 149: testit "$TEST_LABEL - setup root dir" create_dir tmp tmp.$$`, `line 150: testit "grant SeRestorePrivilege" $NET rpc rights grant $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER || exit 1`, `line 151: testit "$TEST_LABEL - assign default ACL" $SMBCACLS //$SERVER/tmp tmp.$$ -U $USERNAME%$PASSWORD -S "REVISION:1,OWNER:$SERVER\force_user,GROUP:$SERVER\domusers,ACL:Everyon`, `line 154: testit "$TEST_LABEL - create subdir under root" create_dir $SHARE tmp.$$/subdir`, `line 155: testit "$TEST_LABEL - verify subdir win owner" win_owner_is $SHARE tmp.$$/subdir "$WIN_OWNER_AFTER_CREATE"`, `line 156: testit "$TEST_LABEL - verify subdir unix owner" unix_owner_id_is $SHARE tmp.$$/subdir $UNIX_OWNER_AFTER_CREATE`, `line 157: testit "$TEST_LABEL - create file under root" create_file $SHARE tmp.$$/afile`, `line 158: testit "$TEST_LABEL - verify file win owner" win_owner_is $SHARE tmp.$$/afile "$WIN_OWNER_AFTER_CREATE"`, `line 159: testit "$TEST_LABEL - verify file unix owner" unix_owner_id_is $SHARE tmp.$$/afile $UNIX_OWNER_AFTER_CREATE`, `line 160: testit "$TEST_LABEL - change dir owner" set_win_owner $SHARE tmp.$$/subdir "$SERVER\smbget_user"`; plus 9 more.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcacls`, `chown`, `mkdir`, `rm`, `touch`, `grep`, `awk`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcacls, chown, mkdir, rm, touch, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_inherit_owner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_large_acl.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_large_acl.sh

## Purpose
Blackbox/selftest shell script for Samba's large acl behavior. It drives the local test environment through `smbclient`, `smbcacls`, `rm`, `touch`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD SMBCLIENT SMBCACLS PARAMS`. Important routines are `build_files (line 29)`, `cleanup (line 36)`, `test_large_acl (line 43)`. Key harness variables include `SERVER (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `SMBCLIENT (line 16)`, `SMBCACLS (line 17)`, `ADDARGS (line 19)`, `SMBCLIENT (line 20)`, `SMBCACLS (line 21)`.

## Control Flow
The file is 61 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 57: testit "able to retrieve a large ACL if VFS supports it" test_large_acl || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcacls`, `rm`, `touch`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcacls, rm, touch, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_large_acl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_libwbclient_threads.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_libwbclient_threads.sh

## Purpose
Blackbox/selftest shell script for Samba's libwbclient threads behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_libwbclient_threads.sh DOMAIN USERNAME`. Key harness variables include `DOMAIN (line 10)`, `USERNAME (line 11)`.

## Control Flow
The file is 17 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 17: testit "libwbclient-threads" "$BINDIR/stress-nss-libwbclient" "$DOMAIN/$USERNAME"`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_libwbclient_threads.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_list_nt4_trust.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_list_nt4_trust.sh

## Purpose
Blackbox/selftest shell script for Samba's list nt4 trust behavior. It drives the local test environment through `smbclient`, `wbinfo`, `sleep`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `test_trust_wbinfo_m (line 12)`.

## Control Flow
The file is 25 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 23: testit "nt4trust_wbinfo_m" test_trust_wbinfo_m || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `wbinfo`, `sleep`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, wbinfo, sleep, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_list_nt4_trust.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_local_s3.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_local_s3.sh

## Purpose
Blackbox/selftest shell script for Samba's local s3 behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_local_s3.sh`.

## Control Flow
The file is 39 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 20: testit "talloctort" $VALGRIND $BINDIR/talloctort ||`, `line 26: testit "replace_testsuite" $VALGRIND $BINDIR/replace_testsuite ||`, `line 30: testit "tdbtorture" $VALGRIND $BINDIR/tdbtorture ||`, `line 36: testit "smbconftort" $VALGRIND $BINDIR/smbconftort $CONFIGURATION ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_local_s3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_ads_kerberos.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_ads_kerberos.sh

## Purpose
Blackbox/selftest shell script for Samba's net ads kerberos behavior. It drives the local test environment through `net`, `klist`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_ads_kerberos.sh USERNAME REALM PASSWORD PREFIX`. Key harness variables include `USERNAME (line 10)`, `REALM (line 11)`, `PASSWORD (line 12)`, `PREFIX (line 13)`, `ADDARGS (line 15)`, `KLIST (line 18)`, `KLIST (line 20)`, `PACFILE (line 27)`, `KRB5CCNAME_PATH (line 29)`, `KRB5CCNAME (line 32)`; plus 1 more.

## Control Flow
The file is 178 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 40: testit "net_ads_kerberos_kinit" \`, `line 46: testit "net_ads_kerberos_kinit (KRB5CCNAME env set)" \`, `line 50: testit "klist env $KRB5CCNAME" \`, `line 56: testit "net_ads_kerberos_kinit (with --use-krb5-ccache)" \`, `line 61: testit "klist --use-krb5-ccache $KRB5CCNAME_PATH" \`, `line 67: testit "net_ads_kerberos_kinit (-P)" \`, `line 73: testit "net_ads_kerberos_kinit (-P and KRB5CCNAME env set)" \`, `line 77: testit "klist env $KRB5CCNAME" \`, `line 83: testit "net_ads_kerberos_kinit (-P with --use-krb5-ccache)" \`, `line 88: testit "klist --use-krb5-ccache $KRB5CCNAME_PATH" \`; plus 7 more.

## State and Persistence Behavior
State touched or modeled by this file includes Kerberos credential caches. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `net`, `klist`, `mkdir`, `rm`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes Kerberos credential caches, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, klist, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_ads_kerberos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cache_samlogon.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_cache_samlogon.sh

## Purpose
Blackbox/selftest shell script for Samba's net cache samlogon behavior. It drives the local test environment through `smbclient`, `net`, `grep`, `awk`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SHARE USER PASS`. Key harness variables include `SERVER (line 13)`, `SHARE (line 14)`, `USER (line 15)`, `PASS (line 16)`.

## Control Flow
The file is 43 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient "Prime samlogon cache" 'exit' //$SERVER/$SHARE -U$USER%$PASS || failed=$(expr $failed + 1)`, `line 29: testit "net cache samlogon list" $BINDIR/net cache samlogon list || failed=$(expr $failed + 1)`, `line 34: testit "net cache samlogon show $usersid" $BINDIR/net cache samlogon show $usersid || failed=$(expr $failed + 1)`, `line 36: testit "net cache samlogon show SID name matches name from list command" test x"$tmp" = x"$username" || failed=$(expr $failed + 1)`, `line 38: testit "net cache samlogon ndrdump $usersid" $BINDIR/net cache samlogon ndrdump $usersid || failed=$(expr $failed + 1)`, `line 41: testit "net cache samlogon ndrdump returns netr_SamInfo3 structure" test $retval -eq 0 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `grep`, `awk`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cache_samlogon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_conf.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_conf.sh

## Purpose
Blackbox/selftest shell script for Samba's net conf behavior. It drives the local test environment through `net`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_conf.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION [rpc]`. Important routines are `log_print (line 43)`, `test_conf_addshare (line 52)`, `test_conf_addshare_existing (line 160)`, `test_conf_addshare_usage (line 182)`, `test_conf_delshare (line 200)`, `test_conf_delshare_empty (line 227)`, `test_conf_delshare_usage (line 239)`, `test_conf_showshare_case (line 256)`, `test_conf_drop (line 294)`, `test_conf_drop_empty (line 322)`, `test_conf_drop_usage (line 348)`, `test_conf_setparm (line 366)`; plus 18 more. Key harness variables include `SCRIPTDIR (line 14)`, `SERVERCONFFILE (line 15)`, `NET (line 16)`, `CONFIGURATION (line 17)`, `RPC (line 18)`, `LOGDIR_PREFIX (line 20)`, `NET (line 28)`, `DIR (line 29)`, `LOG (line 30)`, `NETCMD (line 33)`; plus 9 more.

## Control Flow
The file is 1042 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 926: testit "conf_drop" \`, `line 930: testit "conf_drop_empty" \`, `line 934: testit "conf_drop_usage" \`, `line 938: testit "conf_addshare" \`, `line 942: testit "conf_addshare_existing" \`, `line 946: testit "conf_addshare_usage" \`, `line 950: testit "conf_delshare" \`, `line 954: testit "conf_delshare_empty" \`, `line 958: testit "conf_delshare_usage" \`, `line 962: testit "test_conf_showshare_case" \`; plus 18 more.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `net`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_conf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_cred_change.sh

## Purpose
Blackbox/selftest shell script for Samba's net cred change behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_cred_change.sh CONFIGURATION`.

## Control Flow
The file is 17 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 12: testit "1: change machine secret" $VALGRIND $BINDIR/wbinfo --change-secret || failed=$(expr $failed + 1)`, `line 13: testit "1: validate secret" $VALGRIND $BINDIR/net rpc testjoin "$@" || failed=$(expr $failed + 1)`, `line 14: testit "2: change machine secret" $VALGRIND $BINDIR/wbinfo --change-secret || failed=$(expr $failed + 1)`, `line 15: testit "2: validate secret" $VALGRIND $BINDIR/net rpc testjoin "$@" || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change_at.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_cred_change_at.sh

## Purpose
Blackbox/selftest shell script for Samba's net cred change at behavior. It drives the local test environment through `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_cred_change_at.sh CONFIGURATION`. Important routines are `test_change_machine_secret_at (line 14)`.

## Control Flow
The file is 33 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 30: testit "change machine secret at" test_change_machine_secret_at || failed=$(("$failed" + 1))`, `line 31: testit "validate secret" $VALGRIND "$BINDIR/net rpc testjoin" "$@" || failed=$(("$failed" + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `grep`. Sourced/helper scripts include `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change_at.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_dom_join_fail_dc.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_dom_join_fail_dc.sh

## Purpose
Blackbox/selftest shell script for Samba's net dom join fail dc behavior. It drives the local test environment through `mkdir`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_dom_join_fail_dc.sh  USERNAME PASSWORD DOMAIN PREFIX`. Key harness variables include `DC_USERNAME (line 10)`, `DC_PASSWORD (line 11)`, `DOMAIN (line 12)`, `PREFIX (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 22 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 20: testit_expect_failure "net_dom_join_fail_dc" $VALGRIND $BINDIR/net dom join domain=$DOMAIN account=$USERNAME password=$PASSWORD --option=netbiosname=netrpcjointest --opti`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_dom_join_fail_dc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_lookup.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_lookup.sh

## Purpose
Blackbox/selftest shell script for Samba's net lookup behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER USERNAME PASSWORD NET SAMBA-TOOL DNS-ZONE"`. Key harness variables include `SERVER (line 8)`, `USERNAME (line 10)`, `PASSWORD (line 12)`, `NET (line 14)`, `SAMBATOOL (line 16)`, `DNSZONE (line 18)`, `SITE (line 21)`.

## Control Flow
The file is 54 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 36: testit_grep global 10.53.57.30:389 $NET lookup ldap "$DNSZONE" ||`, `line 40: testit_grep site-aware 1.2.3.4:389 $NET lookup ldap "$DNSZONE" "$SITE" ||`, `line 44: testit_grep global 10.53.57.30:389 $NET lookup ldap "$DNSZONE" nosite ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_lookup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_machine_account.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_machine_account.sh

## Purpose
Blackbox/selftest shell script for Samba's net machine account behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 NET CONFFILE SERVER_IP"`. Important routines are `net_ads_user (line 21)`. Key harness variables include `NET (line 9)`, `CONFFILE (line 11)`, `SERVER_IP (line 13)`.

## Control Flow
The file is 34 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 32: testit "net_ads_user" net_ads_user || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_machine_account.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_misc.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_misc.sh

## Purpose
Blackbox/selftest shell script for Samba's net misc behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_misc.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION`. Important routines are `test_time (line 34)`, `test_lookup (line 41)`, `test_share (line 48)`. Key harness variables include `SCRIPTDIR (line 12)`, `SERVERCONFFILE (line 13)`, `NET (line 14)`, `CONFIGURATION (line 15)`, `PROTOCOL (line 19)`, `PROTOCOL (line 21)`, `NET (line 24)`, `NETTIME (line 25)`, `NETLOOKUP (line 26)`, `NETSHARE (line 27)`; plus 3 more.

## Control Flow
The file is 80 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 55: testit "get the time" \`, `line 59: testit "get the system time" \`, `line 63: testit "get the time zone" \`, `line 67: testit "lookup the PDC" \`, `line 71: testit "lookup the master browser" \`, `line 76: testit "lookup share list" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_misc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry behavior. It drives the local test environment through `net`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_registry.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION RPC`. Important routines are `test_enumerate (line 36)`, `test_getsd (line 43)`, `test_enumerate_nonexisting (line 50)`, `test_enumerate_no_key (line 63)`, `test_create_existing (line 74)`, `test_createkey (line 93)`, `test_deletekey (line 131)`, `test_deletekey_nonexisting (line 178)`, `test_createkey_with_subkey (line 196)`, `test_deletekey_with_subkey (line 225)`, `test_setvalue (line 250)`, `test_deletevalue (line 290)`; plus 2 more. Key harness variables include `SCRIPTDIR (line 17)`, `SERVERCONFFILE (line 18)`, `NET (line 19)`, `CONFIGURATION (line 20)`, `RPC (line 21)`, `NET (line 23)`, `NETREG (line 26)`, `NETREG (line 28)`, `KEY (line 38)`, `KEY (line 45)`; plus 48 more.

## Control Flow
The file is 411 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 332: testit "enumerate HKLM" \`, `line 336: testit "enumerate nonexisting hive" \`, `line 340: testit "enumerate without key" \`, `line 346: testit "getsd HKLM" \`, `line 351: testit "create existing HKLM" \`, `line 355: testit "create key" \`, `line 359: testit "delete key" \`, `line 363: testit "delete^2 key" \`, `line 367: testit "enumerate nonexisting key" \`, `line 371: testit "create key with subkey" \`; plus 9 more.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values.

## Dependencies and Integration Points
External command integrations: `net`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_check.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry_check.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry check behavior. It drives the local test environment through `net`, `grep`, `sed`, `cp`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_net_registry_check.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION DBWRAP_TOOL"`. Important routines are `regcheck (line 30)`, `regrepair (line 37)`, `checkerr (line 43)`, `regchecknrepair (line 51)`, `test_simple (line 71)`, `test_damage (line 83)`, `test_duplicate (line 88)`, `test_slashes (line 96)`, `test_uppercase (line 104)`, `test_strangeletters (line 112)`. Key harness variables include `SCRIPTDIR (line 12)`, `SERVERCONFFILE (line 13)`, `NET (line 14)`, `CONFIGURATION (line 15)`, `DBWRAP_TOOL (line 16)`, `NET (line 18)`, `NETREG (line 20)`, `REGORIG (line 21)`, `REG (line 22)`, `ALLOWEDERR (line 32)`; plus 10 more.

## Control Flow
The file is 145 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 120: testit "simple" \`, `line 124: testit "damages_registry" \`, `line 128: testit "duplicate" \`, `line 132: testit "slashes" \`, `line 136: testit "uppercase" \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values.

## Dependencies and Integration Points
External command integrations: `net`, `grep`, `sed`, `cp`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, grep, sed, cp paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_import.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry_import.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry import behavior. It drives the local test environment through `net`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_registry_import.sh SERVER LOCAL_PATH USERNAME PASSWORD`. Important routines are `test_net_registry_import (line 24)`. Key harness variables include `SERVER (line 10)`, `LOCAL_PATH (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 192 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 183: testit "Test net rpc registry import" \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `net`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_import.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_roundtrip.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry_roundtrip.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry roundtrip behavior. It drives the local test environment through `net`, `rm`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_registry_roundtrip.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION RPC`. Important routines are `conf_roundtrip_step (line 48)`, `conf_roundtrip (line 63)`. Key harness variables include `SCRIPTDIR (line 15)`, `SERVERCONFFILE (line 16)`, `NET (line 17)`, `CONFIGURATION (line 18)`, `RPC (line 19)`, `NET (line 21)`, `NETCMD (line 24)`, `NETCMD (line 26)`, `SED_INVALID_PARAMS (line 38)`, `REGPATH (line 46)`; plus 5 more.

## Control Flow
The file is 158 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 153: testit "conf_roundtrip $conf_file" \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `net`, `rm`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, rm, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_roundtrip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc join behavior. It drives the local test environment through `mkdir`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_join.sh  USERNAME PASSWORD SERVER PREFIX`. Key harness variables include `USERNAME (line 10)`, `PASSWORD (line 11)`, `SERVER (line 12)`, `PREFIX (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 25 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 20: testit "net_rpc_join" $VALGRIND $BINDIR/net rpc join -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private -U$USERN`, `line 21: testit "net_rpc_testjoin" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private `, `line 22: testit "net_rpc_changetrustpw" $VALGRIND $BINDIR/net rpc changetrustpw -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFI`, `line 23: testit "net_rpc_testjoin2" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join_creds.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join_creds.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc join creds behavior. It drives the local test environment through `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_join_creds.sh  DOMAIN USERNAME PASSWORD SERVER PREFIX`. Key harness variables include `DOMAIN (line 10)`, `USERNAME (line 11)`, `PASSWORD (line 12)`, `SERVER (line 13)`, `PREFIX (line 14)`, `ADDARGS (line 16)`.

## Control Flow
The file is 30 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 24: testit "net_rpc_join_creds" $VALGRIND $BINDIR/net rpc join -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private -A`, `line 25: testit "net_rpc_testjoin_creds" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/pr`, `line 26: testit "net_rpc_changetrustpw_creds" $VALGRIND $BINDIR/net rpc changetrustpw -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=`, `line 27: testit "net_rpc_testjoin2_creds" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/p`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join_creds.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_oldjoin.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_oldjoin.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc oldjoin behavior. It drives the local test environment through `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_oldjoin.sh SERVER PREFIX SMB_CONF_PATH`. Important routines are `test_smbpasswd (line 22)`. Key harness variables include `SERVER (line 10)`, `PREFIX (line 11)`, `SMB_CONF_PATH (line 12)`, `OPTIONS (line 20)`.

## Control Flow
The file is 49 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 40: testit "mkdir -p $privatedir" mkdir -p $privatedir || failed=$(expr $failed + 1)`, `line 41: testit "smbpasswd -a -m" \`, `line 44: testit "net_rpc_oldjoin" $VALGRIND $BINDIR/net rpc oldjoin -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`, `line 45: testit "net_rpc_testjoin1" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`, `line 46: testit "net_rpc_changetrustpw" $VALGRIND $BINDIR/net rpc changetrustpw -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`, `line 47: testit "net_rpc_testjoin2" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_oldjoin.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_share_allowedusers.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_share_allowedusers.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc share allowedusers behavior. It drives the local test environment through `net`, `mkdir`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_share_allowedusers.sh  SERVER USERNAME PASSWORD PREFIX`. Key harness variables include `SERVER (line 10)`, `USERNAME (line 11)`, `PASSWORD (line 12)`, `PREFIX (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 49 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 22: testit_grep "net_usersidlist" '^ S-1-1-0$' $VALGRIND $net usersidlist $ADDARGS || failed=$(expr $failed + 1)`, `line 24: testit_grep "net_rpc_share_allowedusers" '^print\$$' $net usersidlist | $VALGRIND $net rpc share allowedusers -S$SERVER -U$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $f`, `line 26: testit_grep "net_rpc_share_allowedusers" '^print\$$' $net usersidlist | $VALGRIND $net rpc share allowedusers -S$SERVER -U$USERNAME%$PASSWORD $ADDARGS - 'print$' || faile`, `line 28: testit_grep "net_rpc_share_allowedusers" '^ user1$' $net usersidlist | $VALGRIND $net rpc share allowedusers -S$SERVER -U$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $fa`, `line 38: subunit_start_test "net_rpc_share_allowedusers"`, `line 42: subunit_pass_test "net_rpc_share_allowedusers"`, `line 46: echo "$multi_userout" | subunit_fail_test "net_rpc_share_allowedusers"`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `net`, `mkdir`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, mkdir, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_share_allowedusers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_tdb.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_tdb.sh

## Purpose
Blackbox/selftest shell script for Samba's net tdb behavior. It drives the local test environment through `smbclient`, `net`, `tdbtool`, `kill`, `sleep`, `touch`; plus 3 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SMBCLIENT SERVER SHARE USER PASS CONFIGURATION LOCALPATH LOCKDIR`. Key harness variables include `SMBCLIENT (line 19)`, `SERVER (line 20)`, `SHARE (line 21)`, `USER (line 22)`, `PASS (line 23)`, `CONFIGURATION (line 24)`, `LOCALPATH (line 25)`, `LOCKDIR (line 26)`, `FILENAME (line 28)`, `SMBCLIENTPID (line 45)`; plus 2 more.

## Control Flow
The file is 121 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 50: testit "Looking for record key of open file" \`, `line 80: testit "Looking for open file in locking.tdb" \`, `line 87: testit "Verify pathname in output" \`, `line 93: testit "Verify filename in output" \`, `line 100: testit "Verify number of share modes in output" \`, `line 104: testit "Complete record dump" \`, `line 110: testit "Verify filename in dump output" \`, `line 115: testit "Verify share path in dump output" \`.

## State and Persistence Behavior
State touched or modeled by this file includes TDB lock records.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `tdbtool`, `kill`, `sleep`, `touch`, `grep`, `awk`, `sed`. Sourced/helper scripts include `# shellcheck source=testprogs/blackbox/subunit.sh`, `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes TDB lock records, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, tdbtool, kill, sleep, touch, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_tdb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_usershare.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_usershare.sh

## Purpose
Blackbox/selftest shell script for Samba's net usershare behavior. It drives the local test environment through `smbclient`, `net`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_usershare.sh SERVER SERVER_IP DOMAIN USERNAME PASSWORD SMBCLIENT <smbclient arguments>`. Important routines are `test_smbclient (line 30)`, `test_net_usershare (line 47)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `ADDARGS (line 16)`.

## Control Flow
The file is 83 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 30: test_smbclient()`, `line 71: testit "create usershare dir for $samba_usershare_name" mkdir --mode=0755 --verbose $samba_usershare_path || failed=$(expr $failed + 1)`, `line 77: test_smbclient "smbclient to $samba_usershare_name" "$samba_usershare_name" 'ls' -U$USERNAME%$PASSWORD || failed=$(expr $failed + 1)`, `line 81: testit "remove usershare dir for $samba_usershare_name" rm -rf $samba_usershare_path || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes live daemon control messages, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_usershare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_netfileenum.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_netfileenum.sh

## Purpose
Blackbox/selftest shell script for Samba's netfileenum behavior. It drives the local test environment through `smbclient`, `rpcclient`, `net`, `kill`, `sleep`, `mkfifo`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: $0 \`. Key harness variables include `SMBCLIENT (line 13)`, `RPCCLIENT (line 15)`, `NET (line 17)`, `SERVER (line 19)`, `SHARE (line 21)`, `SAMBA_DEPRECATED_SUPPRESS (line 25)`, `CLI_FORCE_INTERACTIVE (line 38)`, `CLIENT_PID (line 43)`, `FILE (line 52)`, `RC (line 69)`.

## Control Flow
The file is 84 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 58: testit "Create builtin\\administrators group" \`, `line 62: testit "Add ${USER} to builtin\\administrators" \`, `line 70: testit "netfileenum" test $RC = 0 || failed=$((failed + 1))`, `line 75: testit "Remove ${USER} from builtin\\administrators" \`, `line 79: testit "Remove builtin\\administrators group" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rpcclient`, `net`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rpcclient, net, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_netfileenum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_nt4_trust.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_nt4_trust.sh

## Purpose
Blackbox/selftest shell script for Samba's nt4 trust behavior. It drives the local test environment through `smbclient`, `wbinfo`, `sleep`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `test_trust_wbinfo_m (line 12)`, `test_trust_smbclient (line 23)`.

## Control Flow
The file is 31 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: testit "nt4trust_wbinfo_m" test_trust_wbinfo_m || failed=$(expr $failed + 1)`, `line 29: testit "nt4trust_smbclient" test_trust_smbclient || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `wbinfo`, `sleep`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, wbinfo, sleep, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_nt4_trust.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_offline.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_offline.sh

## Purpose
Blackbox/selftest shell script for Samba's offline behavior. It drives the local test environment through `smbclient`, `touch`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_offline SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBCLIENT`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `WORKDIR (line 17)`, `SMBCLIENT (line 18)`, `SMBCLIENT (line 20)`, `ADDARGS (line 21)`.

## Control Flow
The file is 33 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 31: testit "file has offline attribute" test "x$attribs" = "x1000" || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `touch`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, touch, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_offline.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_old_dirlisting.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_old_dirlisting.sh

## Purpose
Blackbox/selftest shell script for Samba's old dirlisting behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 TIMELIMIT SMBCLIENT`. Key harness variables include `TIMELIMIT (line 11)`, `SMBCLIENT (line 13)`.

## Control Flow
The file is 28 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 27: testit "listing shares with LANMAN1" test ${count} -le 100 ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_old_dirlisting.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_open_eintr.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_open_eintr.sh

## Purpose
Blackbox/selftest shell script for Samba's open eintr behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_open_eintr.sh \`. Key harness variables include `CONF (line 13)`, `SMBCLIENT (line 15)`, `SMBCONTROL (line 17)`, `SERVER (line 19)`, `SHARE (line 21)`, `SAMBA_DEPRECATED_SUPPRESS (line 25)`, `CLI_FORCE_INTERACTIVE (line 41)`, `CLIENT_PID (line 46)`, `GREP_RET (line 69)`.

## Control Flow
The file is 77 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 74: testit "Verify that we could get the file" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_open_eintr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_preserve_case.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_preserve_case.sh

## Purpose
Blackbox/selftest shell script for Samba's preserve case behavior. It drives the local test environment through `smbclient`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_preserve_case.sh SERVER DOMAIN USERNAME PASSWORD PREFIX SMBCLIENT`. Important routines are `test_smbclient (line 34)`. Key harness variables include `SERVER (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `PREFIX (line 18)`, `PROTOCOL_LIST (line 21)`, `PROTOCOL_LIST (line 24)`, `SHARE (line 52)`, `SHARE (line 68)`.

## Control Flow
The file is 86 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 34: test_smbclient()`, `line 41: subunit_start_test "$name"`, `line 45: subunit_pass_test "$name"`, `line 47: echo "$output" | subunit_fail_test "$name"`, `line 55: test_smbclient "Test lowercase ls 1 ($PROTOCOL)" $SHARE "ls 1" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 56: test_smbclient "Test lowercase get 1 ($PROTOCOL)" $SHARE "get 1 LOCAL_1" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 59: test_smbclient "Test lowercase ls A ($PROTOCOL)" $SHARE "ls A" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 60: test_smbclient "Test lowercase get A ($PROTOCOL)" $SHARE "get A LOCAL_A" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 63: test_smbclient "Test lowercase ls z ($PROTOCOL)" $SHARE "ls z" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 64: test_smbclient "Test lowercase get z ($PROTOCOL)" $SHARE "get z LOCAL_Z" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`; plus 7 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_preserve_case.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_printing_var_exp.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_printing_var_exp.sh

## Purpose
Blackbox/selftest shell script for Samba's printing var exp behavior. It drives the local test environment through `smbclient`, `rpcclient`, `sleep`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_printing_var_exp.sh SERVER SERVER_IP DOMAIN USERNAME PASSWORD`. Important routines are `test_var_expansion (line 25)`, `test_empty_queue (line 58)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `DOMAIN (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `ADDARGS (line 16)`, `JOBS (line 64)`.

## Control Flow
The file is 93 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 85: testit "Test variable expansion for '%U', '%u' and '%D'" \`, `line 89: testit "Test queue is empty" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rpcclient`, `sleep`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rpcclient, sleep, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_printing_var_exp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_pthreadpool.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_pthreadpool.sh

## Purpose
Blackbox/selftest shell script for Samba's pthreadpool behavior. It drives the local test environment through `chmod`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 20 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 17: testit "pthreadpool" $VALGRIND $BINDIR/pthreadpooltest ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `chmod`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of chmod paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_pthreadpool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_recycle.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_recycle.sh

## Purpose
Blackbox/selftest shell script for Samba's recycle behavior. It drives the local test environment through `smbclient`, `sleep`, `ln`, `chmod`, `rm`, `touch`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_recycle.sh SERVER SERVER_IP USERNAME PASSWORD LOCAL_PATH PREFIX SMBCLIENT ADDARGS`. Important routines are `do_cleanup (line 38)`, `test_recycle (line 82)`, `test_touch (line 121)`, `test_recycle_crossrename (line 154)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCAL_PATH (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `SMBCLIENT (line 17)`, `ADDARGS (line 19)`, `SAMBA_DEPRECATED_SUPPRESS (line 27)`; plus 2 more.

## Control Flow
The file is 223 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 201: testit "recycle" \`, `line 205: testit "recycle_touch" \`, `line 209: testit "recycle_crossrename" \`, `line 215: testit "check_panic" test $panic_count_0 -eq $panic_count_1 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `sleep`, `ln`, `chmod`, `rm`, `touch`, `grep`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, sleep, ln, chmod, rm, touch, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_recycle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_share.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_registry_share.sh

## Purpose
Blackbox/selftest shell script for Samba's registry share behavior. It drives the local test environment through `smbclient`, `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_registry_share.sh SERVER USERNAME PASSWORD`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`.

## Control Flow
The file is 39 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient \`, `line 31: testit_grep_count \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rpcclient`. Sourced/helper scripts include `. $samba_srcdir/testprogs/blackbox/subunit.sh`, `. $samba_srcdir/testprogs/blackbox/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_share.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_upgrade.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_registry_upgrade.sh

## Purpose
Blackbox/selftest shell script for Samba's registry upgrade behavior. It drives the local test environment through `net`, `mkdir`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_registry_upgrade.sh NET DBWRAP_TOOL"`. Important routines are `registry_check (line 35)`, `registry_upgrade (line 78)`. Key harness variables include `SCRIPT_DIR (line 12)`, `BASE_DIR (line 13)`, `NET (line 15)`, `DBWRAP_TOOL (line 16)`, `DATADIR (line 17)`, `WORKSPACE (line 18)`, `CONFIG_FILE (line 19)`, `CONFIGURATION (line 20)`, `NETCMD (line 22)`, `REGPATH (line 31)`; plus 12 more.

## Control Flow
The file is 192 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 186: testit "registry_upgrade" registry_upgrade || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values, server configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `net`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, server configuration, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_upgrade.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_resolvconf.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_resolvconf.sh

## Purpose
Blackbox/selftest shell script for Samba's resolvconf behavior. It drives the local test environment through `chmod`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 20 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 17: testit "resolvconf" $VALGRIND $BINDIR/resolvconftest ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `chmod`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of chmod paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_resolvconf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rofs.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rofs.sh

## Purpose
Blackbox/selftest shell script for Samba's rofs behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: $0 SERVERCONFFILE SMBCLIENT SERVER SHARE`. Key harness variables include `CONF (line 10)`, `SMBCLIENT (line 12)`, `SERVER (line 14)`, `SHARE (line 16)`.

## Control Flow
The file is 34 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 29: testit_grep "Expect MEDIA_WRITE_PROTECTED" NT_STATUS_MEDIA_WRITE_PROTECTED \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rofs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient.sh ccache binding <rpcclient commands>`. Key harness variables include `KRB5CCNAME (line 10)`, `ADDARGS (line 13)`.

## Control Flow
The file is 19 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 17: testit "rpcclient" $VALGRIND $BINDIR/rpcclient $ADDARGS || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes Kerberos credential caches. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes Kerberos credential caches, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_dfs.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_dfs.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient dfs behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient_dfs.sh USERNAME PASSWORD SERVER RPCCLIENT`. Key harness variables include `USERNAME (line 14)`, `PASSWORD (line 15)`, `SERVER (line 16)`, `RPCCLIENT (line 17)`, `RPCCLIENTCMD (line 19)`, `RC (line 27)`, `RC (line 31)`, `RC (line 36)`, `RC (line 42)`.

## Control Flow
The file is 45 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: testit "dfsversion" test ${RC} -eq 0 || failed=$((failed + 1))`, `line 32: testit "dfsenum" test ${RC} -eq 0 || failed=$((failed + 1))`, `line 37: testit "dfsenumex" test ${RC} -eq 0 || failed=$((failed + 1))`, `line 43: testit "dfsgetinfo" test ${RC} -eq 0 || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. "${incdir}"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_dfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_lookup.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_lookup.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient lookup behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient_lookup.sh USERNAME PASSWORD SERVER RPCCLIENT`. Key harness variables include `USERNAME (line 14)`, `PASSWORD (line 15)`, `SERVER (line 16)`, `RPCCLIENT (line 17)`, `RPCCLIENTCMD (line 19)`, `RC (line 27)`, `RC (line 31)`, `RC (line 35)`, `RC (line 39)`.

## Control Flow
The file is 42 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: testit "lookupsids" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 32: testit "lookupsids_level" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 36: testit "lookupnames" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 40: testit "lookupnames_level" test $RC -eq 0 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_lookup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_netsessenum.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_netsessenum.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient netsessenum behavior. It drives the local test environment through `rpcclient`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 DOMAIN ADMIN_USER ADMIN_PASSWORD SERVER RPCCLIENT SMBTORTURE3 SHARE`. Key harness variables include `DOMAIN (line 14)`, `ADMIN_USER (line 15)`, `ADMIN_PASSWORD (line 16)`, `SERVER (line 17)`, `RPCCLIENT (line 18)`, `SMBTORTURE3 (line 19)`, `SHARE (line 20)`, `USERPASS (line 22)`, `RPCCLIENTCMD (line 23)`, `RC (line 34)`; plus 4 more.

## Control Flow
The file is 55 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 35: testit "netsessenum" test $RC = 0 || failed=$(expr $failed + 1)`, `line 40: testit "count1" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 53: testit "count2" test $RC -eq 0 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_netsessenum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_pw_nt_hash.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_pw_nt_hash.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient pw nt hash behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient_pw_nt_hash.sh USERNAME PASSWORD SERVER RPCCLIENT`. Key harness variables include `USERNAME (line 13)`, `PASSWORD (line 14)`, `SERVER (line 15)`, `RPCCLIENT (line 16)`, `HASH (line 18)`, `RPCCLIENTCMD (line 20)`.

## Control Flow
The file is 27 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 25: testit "rpcclient --pw-nt-hash" $RPCCLIENTCMD || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_pw_nt_hash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_samlogon.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_samlogon.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient samlogon behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient_samlogon.sh USERNAME PASSWORD binding <rpcclient commands>`. Important routines are `rpcclient_samlogon_schannel_seal (line 15)`, `rpcclient_samlogon_schannel_sign (line 20)`. Key harness variables include `USERNAME (line 10)`, `PASSWORD (line 11)`, `ADDARGS (line 13)`.

## Control Flow
The file is 32 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 27: testit "rpcclient dsenumdomtrusts" $VALGRIND $BINDIR/rpcclient $ADDARGS -U% -c "dsenumdomtrusts" || failed=$(expr $failed + 1)`, `line 28: testit "rpcclient getdcsitecoverage" $VALGRIND $BINDIR/rpcclient $ADDARGS -U% -c "getdcsitecoverage" || failed=$(expr $failed + 1)`, `line 29: testit "rpcclient samlogon schannel seal" rpcclient_samlogon_schannel_seal $ADDARGS || failed=$(expr $failed +1)`, `line 30: testit "rpcclient samlogon schannel sign" rpcclient_samlogon_schannel_sign $ADDARGS || failed=$(expr $failed +1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_samlogon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclientsrvsvc.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclientsrvsvc.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclientsrvsvc behavior. It drives the local test environment through `rpcclient`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclientsrvsvc.sh USERNAME PASSWORD SERVER RPCCLIENT SHARE1`. Key harness variables include `USERNAME (line 14)`, `PASSWORD (line 15)`, `SERVER (line 16)`, `RPCCLIENT (line 17)`, `SHARE1 (line 18)`, `RPCCLIENTCMD (line 20)`, `SHARENAME (line 22)`, `MAX_USERS (line 23)`, `COMMENT (line 24)`, `RC (line 34)`; plus 10 more.

## Control Flow
The file is 90 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 35: testit "getinfo on S$SHARE1" test $RC = 0 || failed=$(expr $failed + 1)`, `line 39: testit "verifying $SHARE1 path" test -n "$SHAREPATH" ||`, `line 46: testit "netshareadd" test $RC = 0 || failed=$(expr $failed + 1)`, `line 55: testit "verifying comment" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 63: testit "verifying share path" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 69: testit "set csc policy" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 75: testit "verifying csc policy" test $CSC_CACHING_RET -eq 3 ||`, `line 82: testit "deleting share" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 88: testit "querying deleted share" test $RC -eq 1 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclientsrvsvc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sacl_set_get.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_sacl_set_get.sh

## Purpose
Blackbox/selftest shell script for Samba's sacl set get behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD SMBTORTURE3 NET SHARE"`. Important routines are `sacl_set_get (line 26)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `SMBTORTURE3 (line 17)`, `NET (line 18)`, `SHARE (line 19)`.

## Control Flow
The file is 45 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 37: testit "grant SeSecurityPrivilege" $NET rpc rights grant $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 40: testit "SACL set_get" sacl_set_get || failed=$(expr $failed + 1)`, `line 43: testit "revoke SeSecurityPrivilege" $NET rpc rights revoke $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sacl_set_get.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_server_addresses.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_server_addresses.sh

## Purpose
Blackbox/selftest shell script for Samba's server addresses behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
This file is mostly straight-line script code with its interface defined by positional arguments and environment variables.

## Control Flow
The file is 32 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 11: testit_grep_count \`, `line 16: testit_grep_count \`, `line 21: testit_expect_failure_grep \`, `line 27: testit \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_server_addresses.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_shadow_copy.sh

## Purpose
Blackbox/selftest shell script for Samba's shadow copy behavior. It drives the local test environment through `smbclient`, `ln`, `mkdir`, `rm`, `touch`, `grep`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_shadow_copy SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBCLIENT PARAMS`. Important routines are `build_files (line 49)`, `build_snapshots (line 97)`, `test_count_versions (line 137)`, `test_fetch_snap_file (line 211)`, `test_fetch_snap_dir (line 225)`, `test_shadow_copy_fixed (line 244)`, `test_shadow_copy_everywhere (line 299)`, `test_shadow_copy_format (line 373)`, `test_missing_basedir (line 397)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `WORKDIR (line 18)`, `SMBCLIENT (line 19)`, `ADDARGS (line 21)`, `SMBCLIENT (line 22)`.

## Control Flow
The file is 458 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 270: testit "$msg - regular file" \`, `line 274: testit "$msg - regular file in subdir" \`, `line 278: testit "$msg - regular file in case insensitive subdir" \`, `line 282: testit "$msg - local symlink" \`, `line 286: testit "$msg - abs symlink outside" \`, `line 290: testit "$msg - rel symlink outside" \`, `line 294: testit "$msg - list directory" \`, `line 312: testit "snapshots in each dir - regular file" \`, `line 316: testit "snapshots in each dir - regular file in subdir" \`, `line 320: testit "snapshots in each dir - local symlink (but outside snapshot)" \`; plus 13 more.

## State and Persistence Behavior
State touched or modeled by this file includes snapshot directories. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `ln`, `mkdir`, `rm`, `touch`, `grep`, `awk`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes snapshot directories, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, ln, mkdir, rm, touch, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy_torture.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_shadow_copy_torture.sh

## Purpose
Blackbox/selftest shell script for Samba's shadow copy torture behavior. It drives the local test environment through `smbclient`, `smbtorture`, `ln`, `mkdir`, `rm`, `touch`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_shadow_copy SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBTORTURE SMBCLIENT`. Important routines are `build_files (line 33)`, `build_snapshots (line 45)`, `build_stream_on_snapshot (line 59)`, `test_shadow_copy_write (line 66)`, `test_shadow_copy_stream (line 86)`, `test_shadow_copy_openroot (line 115)`, `test_shadow_copy_fix_inodes (line 134)`, `build_hiddenfile (line 152)`, `test_hiddenfile (line 172)`, `test_shadow_copy_listdir_fix_inodes (line 193)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `WORKDIR (line 18)`, `SMBTORTURE (line 19)`, `SMBCLIENT (line 20)`, `SNAPSHOT (line 26)`.

## Control Flow
The file is 227 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 76: testit "writing to shadow copy of a file" \`, `line 96: subunit_start_test msg`, `line 97: subunit_skip_test msg <<EOF`, `line 103: testit "reading stream of a shadow copy of a file" \`, `line 125: testit "opening shadow copy root of share" \`, `line 203: testit "$msg" \`, `line 221: testit "fix inodes with hardlink" test_shadow_copy_fix_inodes || failed=$(expr $failed + 1)`, `line 223: testit "Test reading DOS attribute" test_hiddenfile || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes snapshot directories. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbtorture`, `ln`, `mkdir`, `rm`, `touch`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes snapshot directories, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbtorture, ln, mkdir, rm, touch, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy_torture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shareenum.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_shareenum.sh

## Purpose
Blackbox/selftest shell script for Samba's shareenum behavior. It drives the local test environment through `rpcclient`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD RPCCLIENT`. Important routines are `user_see_share (line 21)`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `RPCCLIENT (line 15)`, `RPCCLIENT (line 16)`.

## Control Flow
The file is 31 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: testit "$USERNAME sees tmp" user_see_share $USERNAME tmp`, `line 29: testit "$USERNAME sees valid-users-tmp" user_see_share $USERNAME valid-users-tmp`, `line 30: testit "force_user sees tmp" user_see_share force_user tmp`, `line 31: testit_expect_failure "force_user does not see valid-users-tmp" user_see_share force_user valid-users-tmp`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shareenum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sharesec.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_sharesec.sh

## Purpose
Blackbox/selftest shell script for Samba's sharesec behavior. It drives the local test environment through `net`, `sharesec`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_sharesec.sh SERVERCONFFILE SHARESEC NET SHARE`. Key harness variables include `CONF (line 17)`, `SHARESEC (line 18)`, `NET (line 19)`, `SHARE (line 20)`, `CMD (line 22)`, `NET_CMD (line 23)`, `COUNT (line 33)`, `ACL (line 35)`, `OWNER (line 38)`, `GROUP (line 41)`; plus 17 more.

## Control Flow
The file is 148 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 30: testit "Set new ACL" $CMD --replace S-1-1-0:ALLOWED/0x0/READ ||`, `line 32: testit "Query new ACL" $CMD --view || failed=$(expr $failed + 1)`, `line 34: testit "Verify new ACL count" test $COUNT -eq 1 || failed=$(expr $failed + 1)`, `line 36: testit "Verify new ACL" test $ACL = S-1-1-0:ALLOWED/0x0/READ`, `line 39: testit "Verify empty OWNER" test "$OWNER" = "OWNER:" ||`, `line 42: testit "Verify empty GROUP" test "$GROUP" = "GROUP:" ||`, `line 45: testit "Verify control flags" test "$CONTROL" = "SR|DP" ||`, `line 48: testit "Add second ACL entry" $CMD --add S-1-5-32-544:ALLOWED/0x0/FULL ||`, `line 50: testit "Query ACL with two entries" $CMD --view ||`, `line 53: testit "Verify ACL count with two entries" test $COUNT -eq 2 ||`; plus 33 more.

## State and Persistence Behavior
State touched or modeled by this file includes share security descriptors.

## Dependencies and Integration Points
External command integrations: `net`, `sharesec`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes share security descriptors, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, sharesec, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sharesec.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_lanman_plaintext.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb1_lanman_plaintext.sh

## Purpose
Blackbox/selftest shell script for Samba's smb1 lanman plaintext behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smb1_lanman_plaintext.sh SERVER USERNAME PASSWORD`. Key harness variables include `SERVER (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`.

## Control Flow
The file is 63 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 27: test_smbclient "test_default" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 37: test_smbclient_expect_failure "test_lm_fail" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 46: test_smbclient "test_lm_ok" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 56: test_smbclient_expect_failure "test_plaintext_fail_local" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 59: test_smbclient "test_plaintext_ok" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_lanman_plaintext.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_shadow_copy_torture.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb1_shadow_copy_torture.sh

## Purpose
Blackbox/selftest shell script for Samba's smb1 shadow copy torture behavior. It drives the local test environment through `smbtorture`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_shadow_copy SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBTORTURE`. Important routines are `build_files (line 32)`, `build_snapshots (line 41)`, `test_shadow_copy_openroot (line 53)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `WORKDIR (line 18)`, `SMBTORTURE (line 19)`, `SNAPSHOT (line 25)`.

## Control Flow
The file is 77 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 63: testit "opening shadow copy root of share over SMB1" \`.

## State and Persistence Behavior
State touched or modeled by this file includes snapshot directories. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbtorture`, `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes snapshot directories, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbtorture, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_shadow_copy_torture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_system_security.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb1_system_security.sh

## Purpose
Blackbox/selftest shell script for Samba's smb1 system security behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD SMBTORTURE3 NET SHARE"`. Important routines are `smb1_system_security (line 25)`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `SMBTORTURE3 (line 16)`, `NET (line 17)`, `SHARE (line 18)`.

## Control Flow
The file is 44 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 36: testit "grant SeSecurityPrivilege" $NET rpc rights grant $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 39: testit "smb1-system-security" smb1_system_security || failed=$(expr $failed + 1)`, `line 42: testit "revoke SeSecurityPrivilege" $NET rpc rights revoke $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_system_security.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb2_not_casesensitive.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb2_not_casesensitive.sh

## Purpose
Blackbox/selftest shell script for Samba's smb2 not casesensitive behavior. It drives the local test environment through `smbclient`, `rm`, `touch`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smb2_not_casesensitive SERVER SERVER_IP USERNAME PASSWORD LOCAL_PATH SMBCLIENT`. Important routines are `test_access_with_different_case (line 26)`, `test_rename (line 48)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `LOCAL_PATH (line 17)`, `SMBCLIENT (line 18)`.

## Control Flow
The file is 81 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 73: testit "accessing a file with different case succeeds" \`, `line 77: testit "renaming a file with different case succeeds" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`, `touch`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm, touch paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb2_not_casesensitive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_cross_node.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_cross_node.sh

## Purpose
Blackbox/selftest shell script for Samba's smbXsrv client cross node behavior. It drives the local test environment through `smbclient`, `smbstatus`, `jq`, `kill`, `sleep`, `mkfifo`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_smbXsrv_client_cross_node.sh SERVERCONFFILE NODE0 NODE1 SHARENAME`. Important routines are `test_smbclient (line 25)`, `smbstatus_num_sessions (line 50)`. Key harness variables include `CONF (line 12)`, `NODE0 (line 13)`, `NODE1 (line 14)`, `SHARE (line 15)`, `SMBCLIENT (line 17)`, `SMBSTATUS (line 18)`, `UID_WRAPPER_INITIAL_RUID (line 52)`, `CLI_FORCE_INTERACTIVE (line 63)`, `CLIENT_PID (line 72)`.

## Control Flow
The file is 92 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 25: test_smbclient()`, `line 33: subunit_start_test "$name"`, `line 37: subunit_pass_test "$name"`, `line 39: echo "$output" | subunit_fail_test "$name"`, `line 55: testit_grep "step1: smbstatus 0 sessions" '^0$' smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 57: test_smbclient "smbclient against node0[${NODE0}]" "${NODE0}" "${SHARE}" "ls" -U"${DC_USERNAME}"%"${DC_PASSWORD}" \`, `line 61: testit_grep "step2: smbstatus 0 sessions" '^0$' smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 66: testit "start backgroup smbclient against node0[${NODE0}]" true || failed=$(expr $failed + 1)`, `line 76: testit "sleep 1 second" true || failed=$(expr $failed + 1)`, `line 79: testit_grep "step3: smbstatus 1 session" '^1$' smbstatus_num_sessions || failed=$(expr $failed + 1)`; plus 2 more.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `jq`, `kill`, `sleep`, `mkfifo`, `rm`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, jq, kill, sleep, mkfifo, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_cross_node.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_ctdb_registered_ips.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_ctdb_registered_ips.sh

## Purpose
Blackbox/selftest shell script for Samba's smbXsrv client ctdb registered ips behavior. It drives the local test environment through `smbclient`, `smbstatus`, `ctdb`, `jq`, `kill`, `sleep`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_smbXsrv_client_ctdb_registered_ips.sh SERVERCONFFILE CTDB_IFACE_IP SHARENAME`. Important routines are `test_smbclient (line 26)`, `smbstatus_num_sessions (line 53)`, `ctdb_add_public_ip (line 59)`, `ctdb_ip (line 65)`, `ctdb_gettickles (line 70)`, `ctdb_reload_public_ips (line 75)`. Key harness variables include `CONF (line 12)`, `CTDB_IFACE_IP (line 13)`, `SHARE (line 14)`, `SMBCLIENT (line 16)`, `SMBSTATUS (line 17)`, `CTDB (line 18)`, `TIMELIMIT (line 19)`, `UID_WRAPPER_INITIAL_RUID (line 56)`, `UID_WRAPPER_INITIAL_RUID (line 61)`, `UID_WRAPPER_INITIAL_RUID (line 62)`; plus 7 more.

## Control Flow
The file is 159 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient()`, `line 34: subunit_start_test "$name"`, `line 38: subunit_pass_test "$name"`, `line 40: echo "$output" | subunit_fail_test "$name"`, `line 81: testit_grep_count "step1: smbstatus 0 sessions" '^0$' 1 smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 83: test_smbclient "step2: smbclient against node0[${CTDB_IFACE_IP}]" "${CTDB_IFACE_IP}" "${SHARE}" "ls" -U"${DC_USERNAME}"%"${DC_PASSWORD}" \`, `line 87: testit_grep_count "step2: smbstatus 0 sessions" '^0$' 1 smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 92: testit "step3: start backgroup smbclient against node0[${CTDB_IFACE_IP}]" true || failed=$(expr $failed + 1)`, `line 102: testit_grep_count "step3: smbclient1-stdout" 'Try "help" to get a list of possible commands.' 1 $TIMELIMIT 15 head -1 smbclient1-stdout || failed=$(expr $failed + 1)`, `line 104: testit_grep_count "step3: smbstatus 1 session" '^1$' 1 smbstatus_num_sessions || failed=$(expr $failed + 1)`; plus 21 more.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, cluster public IP/tickle state. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `ctdb`, `jq`, `kill`, `sleep`, `mkfifo`, `rm`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, cluster public IP/tickle state, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, ctdb, jq, kill, sleep, mkfifo, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_ctdb_registered_ips.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_dead_rec.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_dead_rec.sh

## Purpose
Blackbox/selftest shell script for Samba's smbXsrv client dead rec behavior. It drives the local test environment through `smbclient`, `smbstatus`, `kill`, `mkfifo`, `rm`, `grep`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_smbXsrv_client_dead_rec.sh SERVERCONFFILE IP SHARENAME`. Key harness variables include `CONF (line 12)`, `SERVER (line 13)`, `SHARE (line 14)`, `SMBCLIENT (line 16)`, `SMBSTATUS (line 17)`, `SMBD_LOG_FILE (line 19)`, `SMBD_LOG_FILE (line 21)`, `SMBD_LOG_FILE (line 23)`, `CLI_FORCE_INTERACTIVE (line 41)`, `CLIENT_PID (line 48)`; plus 1 more.

## Control Flow
The file is 76 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 73: testit "check_panic" test "$panic_count_0" -eq "$panic_count_1" ||`.

## State and Persistence Behavior
State touched or modeled by this file includes cluster client records, named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `kill`, `mkfifo`, `rm`, `grep`, `awk`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes cluster client records, named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, kill, mkfifo, rm, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_dead_rec.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb_prometheus_endpoint.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb_prometheus_endpoint.sh

## Purpose
Blackbox/selftest shell script for Samba's smb prometheus endpoint behavior. It drives the local test environment through `smbclient`, `smbstatus`, `curl`, `kill`, `sleep`, `rm`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD LOCK_DIR PREFIX SMBPROMETHEUS SMBCLIENT CONFIGURATION PROTOCOL"`. Important routines are `start_smbprometheus (line 34)`, `stop_smbprometheus (line 63)`, `make_some_smb_ops (line 76)`, `test_smbprometheus_tcon (line 101)`, `test_smbprometheus_info (line 124)`, `test_smbprometheus_many (line 147)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCK_DIR (line 14)`, `PREFIX (line 15)`, `SMBPROMETHEUS (line 16)`, `SMBCLIENT (line 17)`, `CONFIGURATION (line 18)`, `PROTOCOL (line 19)`; plus 6 more.

## Control Flow
The file is 189 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 177: testit "test_smbprometheus_tcon" \`, `line 181: testit "test_smbprometheus_info" \`, `line 185: testit "test_smbprometheus_many" \`.

## State and Persistence Behavior
State touched or modeled by this file includes profile metrics database. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `curl`, `kill`, `sleep`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes profile metrics database, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, curl, kill, sleep, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb_prometheus_endpoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_auth.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_auth.sh

## Purpose
Blackbox/selftest shell script for Samba's smbclient auth behavior. It drives the local test environment through `smbclient`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smbclient_auth.sh SERVER SERVER_IP USERNAME PASSWORD SMBCLIENT <smbclient arguments>`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `SMBCLIENT (line 16)`, `SMBCLIENT (line 17)`, `ADDARGS (line 19)`, `IPV6LITERAL (line 31)`.

## Control Flow
The file is 47 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 7: Usage: test_smbclient_auth.sh SERVER SERVER_IP USERNAME PASSWORD SMBCLIENT <smbclient arguments>`, `line 32: testit "smbclient //${IPV6LITERAL}/tmpguest as user" $SMBCLIENT //${IPV6LITERAL}/tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -c quit $ADDARGS || failed=$(expr $failed +`, `line 33: testit "smbclient //${IPV6LITERAL}./tmpguest as user" $SMBCLIENT //${IPV6LITERAL}./tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -c quit $ADDARGS || failed=$(expr $failed`, `line 35: testit "smbclient //${SERVER_IP}/tmpguest as user" $SMBCLIENT //${SERVER_IP}/tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -p 139 -c quit $ADDARGS || failed=$(expr $faile`, `line 37: testit "smbclient //$SERVER/guestonly as user" $SMBCLIENT //$SERVER/guestonly $CONFIGURATION -U$USERNAME%$PASSWORD -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr `, `line 38: testit "smbclient //$SERVER/guestonly as anon" $SMBCLIENT //$SERVER/guestonly $CONFIGURATION -U% -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $failed + 1)`, `line 39: testit "smbclient //$SERVER/tmpguest as user" $SMBCLIENT //$SERVER/tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $f`, `line 40: testit "smbclient //$SERVER/tmpguest as anon" $SMBCLIENT //$SERVER/tmpguest $CONFIGURATION -U% -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $failed + 1)`, `line 41: testit "smbclient //$SERVER/forceuser as user" $SMBCLIENT //$SERVER/forceuser $CONFIGURATION -U$USERNAME%$PASSWORD -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr `, `line 42: testit "smbclient //$SERVER/forceuser as anon" $SMBCLIENT //$SERVER/forceuser $CONFIGURATION -U% -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $failed + 1)`; plus 4 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_auth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_basic.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_basic.sh

## Purpose
Blackbox/selftest shell script for Samba's smbclient basic behavior. It drives the local test environment through `smbclient`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smbclient_basic.sh SERVER SERVER_IP DOMAIN USERNAME PASSWORD SMBCLIENT <smbclient arguments>`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `CONFIGURATION (line 17)`, `ADDARGS (line 19)`, `SAVE_CONFIGURATION (line 41)`, `CONFIGURATION (line 42)`, `CONFIGURATION (line 44)`.

## Control Flow
The file is 47 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 7: Usage: test_smbclient_basic.sh SERVER SERVER_IP DOMAIN USERNAME PASSWORD SMBCLIENT <smbclient arguments>`, `line 26: test_smbclient "smbclient as $DOMAIN\\$USERNAME" 'ls' "//$SERVER/tmp" -U$DOMAIN\\$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $failed + 1)`, `line 28: test_smbclient "smbclient as $DOMAIN/$USERNAME" 'ls' "//$SERVER/tmp" -U$DOMAIN/$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $failed + 1)`, `line 31: test_smbclient "smbclient as $DOMAIN+$USERNAME" 'ls' "//$SERVER/tmp" -U$DOMAIN+$USERNAME%$PASSWORD $ADDARGS --option=winbindseparator=+ || failed=$(expr $failed + 1)`, `line 43: test_smbclient "smbclient as $DOMAIN+$USERNAME" 'ls' "//$SERVER/tmp" -U$DOMAIN+$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption.sh

## Purpose
Blackbox/selftest shell script for Samba's smbclient encryption behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smbclient_encryption.sh USERNAME PASSWORD SERVER SMBCLIENT TARGET`. Key harness variables include `USERNAME (line 10)`, `PASSWORD (line 11)`, `SERVER (line 12)`, `SMBCLIENT (line 13)`, `TARGET (line 14)`.

## Control Flow
The file is 72 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 5: Usage: test_smbclient_encryption.sh USERNAME PASSWORD SERVER SMBCLIENT TARGET`, `line 38: testit "smbclient.smb3.client.encrypt.desired[//$SERVER/enc_desired]" $SMBCLIENT //$SERVER/enc_desired -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=desired -c '`, `line 40: testit "smbclient.smb3.client.encrypt.desired[//$SERVER/tmpenc]" $SMBCLIENT //$SERVER/tmpenc -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=desired -c 'ls; quit' `, `line 42: testit_expect_failure "smbclient.smb3.client.encrypt.desired[//$SERVER/tmpenc]" $SMBCLIENT //$SERVER/tmpenc -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=desired`, `line 44: testit "smbclient.smb3.client.encrypt.desired[//$SERVER/tmp]" $SMBCLIENT //$SERVER/tmp -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=desired -c 'ls; quit' || fai`, `line 46: testit "smbclient.smb3.client.encrypt.if_required[//$SERVER/enc_desired]" $SMBCLIENT //$SERVER/enc_desired -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=if_requi`, `line 48: testit "smbclient.smb3.client.encrypt.if_required[//$SERVER/tmpenc]" $SMBCLIENT //$SERVER/tmpenc -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=if_required -c 'ls`, `line 50: testit_expect_failure "smbclient.smb3.client.encrypt.if_required[//$SERVER/tmpenc]" $SMBCLIENT //$SERVER/tmpenc -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=if_`, `line 52: testit "smbclient.smb3.client.encrypt.if_required[//$SERVER/tmp]" $SMBCLIENT //$SERVER/tmp -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=if_required -c 'ls; quit`, `line 55: testit "smbclient.smb3.client.encrypt.required[//$SERVER/enc_desired]" $SMBCLIENT //$SERVER/enc_desired -U$USERNAME%$PASSWORD -mSMB3 --option=clientsmbencrypt=required -c`; plus 9 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption.sh -->
