# sources/distributed-fs/lizardfs/src/master/changelog.cc

Purpose: master/metalogger changelog writer and rotation manager.

Important APIs/functions: `changelog_init`, `changelog_get_back_logs_config_value`, `changelog_rotate`, `changelog`, `changelog_flush`, `changelog_disable_flush`, `changelog_enable_flush`, and reload callback `changelog_reload`.

Control flow: initialization stores filename and allowed `BACK_LOGS` bounds, validates config, and registers reload. `changelog` lazily opens the file in append mode, writes `<version>: <entry>`, and flushes unless disabled. Rotation closes the file and either rotates backlogs or unlinks the active file when retention is zero.

State and persistence: global filename, min/max, current backlog count, `FILE *fd`, and flush flag; persists metadata changes to changelog files.

Dependencies and integration: uses config, event-loop reload, `rotateFiles`, logging, and metadata modules that call `changelog`.

Risks: if opening fails, metadata changes are only logged as lost to syslog. Flush disabling improves performance but increases loss risk until re-enabled. Bound validation happens at init; reload uses min/max getter.

Test signals: no direct tests in this subset; behavior is critical to metadata recovery integration.
