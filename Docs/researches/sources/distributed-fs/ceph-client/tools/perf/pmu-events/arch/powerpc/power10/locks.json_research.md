# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/locks.json

## Purpose
This 4-entry POWER10 locks file focuses on conditional store (`STCX`) behavior used in lock acquisition. It provides failed, total finished, pass finished, and nest-successfully completed STCX event aliases.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The file distinguishes `PM_STCX_FAIL_FIN`, `PM_STCX_FIN`, `PM_STCX_PASS_FIN`, and `PM_STCX_SUCCESS_CMPL`, where the last specifically counts pass status returned from the nest.

## Control Flow And Integration
The POWER10 generated PMU table exposes these names for direct lock-contention analysis. They may be paired with load-reserve events from other files and with application-level synchronization profiling.

## State, Dependencies, Risks, And Tests
The file is static. Risks include confusing pass/finish/success semantics, assuming the four counters are mutually exclusive without checking PMU documentation, and event-code errors in a tiny table where every row matters. Test signals include JSON validity, generated alias checks, and lock-contention microbenchmarks comparing STCX failure and success counts.
