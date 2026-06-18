<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-rmcell.pl -->
# sources/distributed-fs/openafs/src/tests/afs-rmcell.pl

## Purpose
Root-only cleanup utility that removes local OpenAFS cell configuration, databases, logs, local state, and volume files for a selected vice partition.

## Important APIs, Types, And Functions
Uses `OpenAFS::Dirpath`, `OpenAFS::OS`, `OpenAFS::ConfigUtils::run`, `Term::ReadLine`, `Getopt::Long`, and `Pod::Usage`. Options are `--debug`, `--help`, `--batch`, `--partition-id`, and `--ostype`.

## Control Flow
Parses options, checks root, validates the partition abbreviation, prompts for the literal confirmation word `destroy` unless batch mode is used, creates an OS helper, configures the client, stops client/fileserver services, force-stops the client, and removes database, BosConfig, logs, local files, cell config, KeyFile, krb.conf, client CellServDB/ThisCell, and `/vicep<id>` volume data/locks.

## State And Persistence
Deletes persistent OpenAFS state from AFS db/config/local/log directories and one vice partition. It does not remove arbitrary nonstandard partition names.

## Dependencies And Integration Points
Complements `afs-newcell.pl`; the new-cell script points users to this cleanup when old config files exist.

## Risks And Test Signals
Highly destructive by design. Batch mode bypasses confirmation. Removal uses OS helper glob behavior, so quoting/platform semantics matter. Success signal is stopped services and missing config/database/volume files before rerunning `afs-newcell.pl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-rmcell.pl -->
