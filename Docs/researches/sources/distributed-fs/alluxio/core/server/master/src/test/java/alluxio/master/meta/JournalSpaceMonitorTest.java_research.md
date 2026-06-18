# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/JournalSpaceMonitorTest.java

Purpose: tests Linux journal disk-space monitoring, disk-info parsing, and warning logging.

Important APIs/types/functions: uses `JournalSpaceMonitor`, `JournalDiskInfo`, `CommandReturn`, `TestLoggerRule`, `OSUtils.isLinux`, and Mockito spies over `getRawDiskInfo`.

Control flow: class-level assumption skips non-Linux platforms. `testNonExistentJournalPath` expects an invalid path to fail construction. `testSuccessfulInfo` stubs a `df`-style output and verifies disk path, total/used/available byte conversions from 1024-blocks, and percent available. `testFailedInfo` stubs `getRawDiskInfo` to throw and expects propagation. Logging tests create monitors with thresholds above or below the parsed free percentage, call `heartbeat`, and assert whether the warning regex was logged.

State and persistence behavior: no persistent state beyond the monitored path; command output is mocked.

Dependencies and integration points: integrates heartbeat executor contract, shell command parsing, Alluxio wire disk info, and log4j warning capture.

Risks: parser coverage uses one exact `df` output shape. Linux-only assumption avoids portability but leaves non-Linux behavior untested.

Test signals: good focused signal for threshold calculation and warning behavior on the supported Linux path.
