<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stress_code_patching.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stress_code_patching.sh

Purpose: Shell stress test for spurious faults while kernel code is being mapped/patched through ftrace. It repeatedly toggles function tracing and watches for ftrace bug reports.

Important APIs and types: Defines `TIMEOUT`, discovers debugfs tracing paths, checks current trace health, clears dmesg, loops setting `current_tracer` to `function` and `nop`, then inspects dmesg for `ftrace bug`.

Control flow: The script skips if debugfs/tracing is unavailable, aborts if tracing is already corrupted, runs for 30 seconds or until a bug appears, restores `nop`, and returns pass/fail.

State and persistence: It mutates global tracing state and clears/reads the kernel log; those effects are system-wide during the test.

Dependencies and integration points: Depends on debugfs, ftrace, dmesg access, and shell utilities. Integrated as `TEST_PROGS` by the MM Makefile.

Risks: Requires permissions to clear/read dmesg and alter tracing. Running on shared systems can disturb tracing users.

Test signals: Pass prints that mapping kernel memory does not cause spurious faults; failure is any observed ftrace bug marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stress_code_patching.sh -->
