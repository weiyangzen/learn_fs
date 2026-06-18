## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.cc

Purpose: implements cleaner configuration construction and defaults. The constructor stores interval and stale-age durations. `getDefaultConfig()` returns a one-hour run interval and one-week inactivity threshold.

State/dependencies: simple value object using `std::chrono::seconds` and `std::unique_ptr`. Integration is with `BulkRequestProcCleaner` setup.

Risks: defaults are hard-coded and comments are the main policy documentation. Tests should verify the exact default values (`3600`, `604800`) and custom constructor propagation.
