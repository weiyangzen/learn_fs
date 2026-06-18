## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.hh

Purpose: declares the configuration object for proc bulk-request cleanup. It exposes public duration fields for cleanup interval and inactivity age.

Important APIs/state: constructor, `mInterval`, `mBulkReqLastAccessTimeBeforeCleaning`, and `getDefaultConfig()`.

Integration: owned by `BulkRequestProcCleaner`. Risks include mutable public fields and no validation against zero/negative-equivalent durations. Test signals should include default config and edge intervals if caller validation is added.
