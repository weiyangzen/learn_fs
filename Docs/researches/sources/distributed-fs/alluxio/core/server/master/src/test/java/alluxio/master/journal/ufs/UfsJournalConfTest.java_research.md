# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalConfTest.java

Purpose: verifies conversion from Alluxio journal-specific UFS option properties into `UnderFileSystemConfiguration`.

Important APIs/types/functions: uses `UfsJournal.getJournalUfsConf`, `UnderFileSystemConfiguration`, `PropertyKey.Template.MASTER_JOURNAL_UFS_OPTION_PROPERTY`, and `PropertyKey.UNDERFS_LISTING_LENGTH`.

Control flow: `emptyConfiguration` calls `getJournalUfsConf` with no journal UFS overrides and expects empty mount-specific configuration. `nonEmptyConfiguration` formats a journal UFS option key for `underfs.listing.length`, sets it to `10000`, then expects the resulting UFS configuration to return that value and contain exactly one mount-specific entry.

State and persistence behavior: no journal state is created. The only mutable state is global configuration, reset after each test.

Dependencies and integration points: covers the bridge from master journal configuration namespace to UFS mount-specific options.

Risks: tests a single property and type. It does not cover invalid property names, multiple overrides, string-valued options, or precedence against global UFS configuration.

Test signals: concise regression signal that journal UFS option templating is honored and does not create phantom mount-specific config when unset.
