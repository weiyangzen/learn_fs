# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/run.sh

Purpose: generic runtime wrapper for individual LKDTM crash/protection tests.

Important APIs/types/functions: uses debugfs files `/sys/kernel/debug/provoke-crash/DIRECT` and `/sys/kernel/debug/clear_warn_once`, reads `tests.txt`, captures `dmesg`, and reports kselftest skip code `4`.

Control flow: verifies the LKDTM trigger, attempts `modprobe lkdtm`, derives the test name from the script basename, finds the corresponding `tests.txt` line, verifies kernel support, detects commented-out tests, parses expected output and optional `repeat:N`, snapshots dmesg, writes test names to the trigger using `cat` so the shell survives expected crashes, diffs new dmesg output, and greps for success text or `XFAIL`.

State and persistence: temporarily creates log files and may clear WARN_ONCE state. It reads and writes debugfs trigger state and consumes kernel log state.

Dependencies and integration points: root/debugfs/module availability, `tests.txt`, `dmesg`, `comm`, `grep`, `modprobe`, and LKDTM debugfs ABI.

Risks: tests intentionally trigger kernel warnings/oops-like behavior; success detection depends on dmesg wording. Kernel log wraparound can affect matching.

Test signals: success is expected regex present in new dmesg; `XFAIL` converts to skip; missing trigger/test/config produces skip.
