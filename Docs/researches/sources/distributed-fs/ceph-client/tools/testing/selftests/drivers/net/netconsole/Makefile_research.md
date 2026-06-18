<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/Makefile -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/Makefile

Purpose: kselftest makefile registering netconsole shell tests and shared include dependencies.

Important variables/APIs: `TEST_INCLUDES` lists `../../../net/lib.sh` and `../lib/sh/lib_netcons.sh`; `TEST_PROGS` lists basic, cmdline, fragmented message, overflow, resume, sysdata, and torture tests; includes `../../../lib.mk`.

Control flow: no runtime logic; kselftest build/install infrastructure uses the variables to copy and execute scripts.

State/dependencies: depends on relative paths in kselftest tree and lib.mk conventions. Risks are missing new scripts if not added to `TEST_PROGS`, and included helper path drift. Test signals are make/kselftest discovery of all intended scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/Makefile -->
