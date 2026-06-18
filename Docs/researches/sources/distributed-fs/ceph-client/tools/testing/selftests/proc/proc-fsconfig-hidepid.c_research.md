# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-fsconfig-hidepid.c

Purpose: validates new mount API parsing for procfs `hidepid`. It checks that binary `hidepid` configuration is rejected while string values remain accepted.

Important APIs and functions: local wrappers call raw `fsopen()` and `fsconfig()` through `__NR_fsopen` and `__NR_fsconfig`. The test uses `FSCONFIG_SET_BINARY`, `FSCONFIG_SET_STRING`, and close.

Control flow: open a procfs fs context, attempt to set `hidepid` as binary integer 2, require `EINVAL`, then set `"2"` and `"invisible"` string values successfully.

State and persistence: only a transient fs context file descriptor is created. It is closed before exit and no mount is instantiated.

Dependencies and integration: depends on the new mount API and procfs fs_context support. It integrates with selftests as a direct assertion-style C program.

Risks and test signals: failures indicate accidental acceptance of binary hidepid input or broken string option parsing. Environments without fsopen support may fail rather than skip because the program asserts `fsopen("proc")` succeeds.
