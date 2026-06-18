# sources/distributed-fs/moosefs/mfsmaster/changelog.c

`changelog.c` is the master metadata-change logger. It increments metadata versions, formats change records, writes them to durable changelog storage, broadcasts records to metadata-log clients, and keeps bounded in-memory old-change blocks for delayed receivers and metadata sending.

`old_changes_entry` stores version, length, and copied log data. `old_changes_block` stores up to 5000 entries plus aggregate size, minimum timestamp/version, and next pointer. Public operations include `changelog`, `changelog_mr`, `changelog_rotate`, `changelog_get_old_changes`, `changelog_get_minversion`, `changelog_generate_gids`, `changelog_escape_name`, `changelog_init`, and changelog file probes.

`changelog` formats into a static 200000-byte buffer, increments `meta_version`, writes through `changelog_mr`, stores and broadcasts the copied string, and updates `lastchange`. `changelog_mr` delegates to `bgsaver_changelog` in background mode or appends to `changelog.0.mfs` in async/sync foreground modes. `changelog_rotate` prefers background rotation unless forced foreground. `changelog_get_old_changes` locates the block containing the requested version and streams entries up to a limit.

Persistent state is `changelog.0.mfs` and rotated backlog files. Sync mode fsyncs every record; async mode flushes stdio; background mode delegates durability to `bgsaver`. In-memory replay retention is bounded by `CHANGELOG_PRESERVE_SECONDS`, `CHANGELOG_PRESERVE_MB`, `meta_chlog_keep_version`, and `matomlserv_get_min_version`.

Dependencies include `metadata`, `bgsaver`, `main`, `mfslog`, `matomlserv`, `cfg`, and `clocks`. Many mutation modules call `changelog()`, while `matomlserv.c` uses old-change replay for delayed metadata-log clients. Risks are static non-thread-safe buffers, foreground write failures that can log lost changes, format-sensitive version parsing, and subtle old-change pruning accounting. Test signals include version increments, foreground/background persistence, retention pruning, delayed replay, escaping, rotation, and first/last-version parsing from valid and corrupt log files.
