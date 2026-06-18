# sources/distributed-fs/ceph-client/drivers/net/netdevsim/health.c

Purpose: provides devlink health reporter fixtures for netdevsim. One reporter is intentionally empty, while the dummy reporter emits structured diagnostic/dump content and supports recovery failure injection.

Important APIs/types/functions: `nsim_dev_health_init()` creates `empty` and `dummy` reporters plus debugfs files. `nsim_dev_dummy_reporter_recover()`, `_dump()`, and `_diagnose()` implement the dummy reporter. `nsim_dev_health_break_write()` triggers `devlink_health_report()` using a caller-provided break message. `nsim_dev_health_exit()` releases debugfs, saved messages, and reporters.

Control flow: initialization creates reporters before debugfs. Writing `break_health` copies a user string, strips a trailing newline, passes it as private context to devlink health reporting, and frees it. Recovery optionally fails when `fail_recover` is set; otherwise it stores the recovered message. Dump and diagnose populate fmsg fields with scalar, binary, nested, and array data sized by `binary_len`.

State and persistence: `struct nsim_dev_health` stores reporter handles, debugfs root, last recovered message, binary payload length, and the `fail_recover` toggle. State is volatile and freed on exit.

Dependencies and integration: depends on devlink health reporter APIs, debugfs, random bytes, and `nsim_dev`. It is a test integration point for fmsg formatting, recovery callbacks, and devlink health userspace tooling.

Risks: the dummy fmsg builder allocates user-controlled `binary_len` bytes with `__GFP_NOWARN`; very large values can force `-ENOMEM`. Recovery stores only the last break message. The file intentionally lets tests force reporter recovery failure.

Test signals: write `break_health`, inspect devlink health dump/diagnose output, vary `binary_len`, toggle `fail_recover`, and verify reporter destruction leaves no saved message or debugfs entries.
