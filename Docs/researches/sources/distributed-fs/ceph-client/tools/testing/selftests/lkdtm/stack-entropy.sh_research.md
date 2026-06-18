# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/stack-entropy.sh

Purpose: estimates kernel stack offset entropy using LKDTM `REPORT_STACK`.

Important APIs/types/functions: writes `REPORT_STACK` repeatedly to `/sys/kernel/debug/provoke-crash/DIRECT`, follows `dmesg`, parses recent `Stack offset` values, computes a rough bit count with `bc`, and applies kselftest skip code `4`.

Control flow: accepts optional sample count, verifies/modprobes LKDTM, starts `dmesg --follow`, triggers the report loop, kills the follower, counts unique offsets from the last sample window, removes the temporary log, and fails if the observed entropy is below five bits.

State and persistence: creates a temporary log and consumes live kernel log output. It does not restore any kernel state.

Dependencies and integration points: debugfs/LKDTM, root access, `dmesg`, `tac`, `grep`, `awk`, `sort`, `uniq`, `bc`.

Risks: kernel log truncation or concurrent LKDTM messages can skew the sample. The heuristic threshold is coarse and environment-sensitive.

Test signals: skip on missing trigger, fail on fewer than five observed entropy bits, pass otherwise.
