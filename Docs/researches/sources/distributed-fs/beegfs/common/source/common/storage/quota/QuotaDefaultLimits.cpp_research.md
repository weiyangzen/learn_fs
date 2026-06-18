<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.cpp

Purpose: Persists default quota limit values for users and groups.

Important APIs/functions: `loadFromFile` reads and deserializes four default limit counters. `saveToFile` creates parent paths and writes serialized limits. `clearLimits` zeros all defaults and unlinks the store file.

Control flow/state/persistence: Loading uses `open`, `fstat`, `malloc`, single `read`, and `deserialize`. Saving uses `open(O_CREAT|O_TRUNC|O_WRONLY)`, `malloc(serialLen())`, `serialize`, and single `write`. Like `QuotaData`, persistence is truncate-write rather than atomic rename.

Dependencies/integration: Depends on `StorageTk`, `Path`, BeeGFS logger macros, and POSIX file APIs. Integrated with quota configuration state on management/storage services.

Risks/test signals: Tests should cover absent file, corrupt serialized contents, parent path creation, write failure, unlink failure, and clear/reload behavior. Crash during save can leave an empty or partial default-limits file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.cpp -->
