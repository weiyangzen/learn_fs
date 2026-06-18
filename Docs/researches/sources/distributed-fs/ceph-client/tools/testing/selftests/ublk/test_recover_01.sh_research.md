<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_01.sh

## Purpose
Exercises kill-daemon recovery across null, loop, and stripe in buffered/default, no-buffer, and reissue modes.

## Important APIs, Types, and Functions
ublk_run_recover_test or ublk_run_quiesce_recover, run_io_and_recover, _have_feature, _create_backfile.

## Control Flow
Creates data files, launches target/mode combinations in background, waits for each wave, and reports any nonzero helper status through ERR_CODE.

## State and Persistence
Backfiles are temporary; the core state under test is ublk daemon death/quiesce, recovery, and I/O reissue while fio is active.

## Dependencies and Integration Points
fio, test_common.sh run_io_and_recover, ublk recovery support; zero-copy or quiesce feature gates where present.

## Risks and Edge Cases
Parallel background jobs all write ERR_CODE in the shell process context only through function bodies; diagnostics can interleave; skipped feature gates limit coverage on older kernels.

## Test Signals
Pass requires every run_io_and_recover scenario to finish with zero status; fio absence or missing feature returns skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_01.sh -->
