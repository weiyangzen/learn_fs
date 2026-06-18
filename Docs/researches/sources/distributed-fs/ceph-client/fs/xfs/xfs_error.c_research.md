# sources/distributed-fs/ceph-client/fs/xfs/xfs_error.c

Purpose: Provides XFS corruption/error reporting helpers and, in DEBUG builds, sysfs-controlled random error and delay injection.

Important APIs, types, and functions: DEBUG code exposes errortag sysfs attributes and implements errortag init/delete/test/delay/add/add-name/copy/clearall helpers. Always-built reporting functions include `xfs_error_report()`, `xfs_corruption_error()`, `xfs_buf_corruption_error()`, `xfs_buf_verifier_error()`, `xfs_verifier_error()`, and `xfs_inode_verifier_error()`.

Control flow: Errortag sysfs store accepts numeric factors or `default`; tests inject when random selection hits zero; delay tags use `mdelay()`. Reporting functions gate stack traces and hex dumps by `xfs_error_level`, stamp buffer I/O errors for verifier failures, tag alerts, and instruct repair.

State and persistence: Errortag values are in-memory per mount and exposed through sysfs. Reporting mutates buffer error state but does not persist metadata.

Dependencies and integration points: Integrates with XFS sysfs, mount objects, panic-tag alerts, random numbers, buffer/inode verifiers, global error level, and dump helpers.

Risks and test signals: Risks include noisy or insufficient diagnostics, missing buffer error stamping, unsafe delay contexts, stale errortag tables, and debug-only assumptions. Test verifier CRC/corruption paths, sysfs store/show, panic mask, error-level dump thresholds, and non-DEBUG stubs.
