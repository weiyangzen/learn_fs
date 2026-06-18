# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_post_reboot_tests

Purpose: post-reboot validation that pstore persisted crash records and the pre-crash pmsg UUID, then removes the records.

Important APIs and functions: sources `common_tests`; uses `grep /proc/mounts`, `mount -t pstore`, `check_files_exist`, `operate_files`, `grep_end_trace`, and `rm`.

Control flow: skip with code 4 if `reboot_flag` is absent, otherwise remove it, find or mount pstorefs, cd to mount point, verify `dmesg`, `console`, and `pmsg` files exist, check dmesg and console contain end-trace markers, check pmsg contains exactly one test string matching `prev_uuid`, then remove all backend records.

State and persistence: consumes `reboot_flag` and `prev_uuid`; deletes files from pstorefs after validation.

Dependencies and integration: requires pstorefs mount access and persisted crash data from `pstore_crash_test`.

Risks and test signals: exact oops marker matching and backend-specific file naming can vary. Cleanup deletes all `*-${backend}-*` records, which is intrusive on shared machines.
