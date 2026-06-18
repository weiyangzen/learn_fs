<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-newcell.pl -->
# sources/distributed-fs/openafs/src/tests/afs-newcell.pl

## Purpose
Interactive or batch provisioning script for creating an initial test OpenAFS cell with database servers, file server, client startup, root volumes, replicated/unreplicated test volumes, ACLs, and Kerberos/kaserver security initialization.

## Important APIs, Types, And Functions
Defines `prompt`, `mkvol`, and `check_program`. Uses `OpenAFS::ConfigUtils::run/unwind`, `OpenAFS::Dirpath`, `OpenAFS::OS`, `OpenAFS::Auth`, `Getopt::Long`, `Pod::Usage`, and `Socket`. Options control batch/debug/unwind, server, cell, partition, admin principal, Kerberos type/realm/keytab, DAFS mode, and server command options.

## Control Flow
Validates root, absence of prior config/database files, required binaries, keytab/auth mode, hostname forward/reverse lookup, partition id, empty `/vicep<part>`, and stopped server processes. It writes `run-tests.conf`, stops services, configures client files, creates required directories, starts `bosserver -noauth`, sets cell/host/user, starts ptserver/vlserver and optional kaserver, creates security keys/admin, restarts DB servers, starts file services, creates `root.afs`, starts client, authorizes as admin, creates/mounts/releases `root.cell`, creates `user`, `service`, `unrep`, and `rep`, adds RO sites, and clears unwind actions on success.

## State And Persistence
Writes AFS configuration files, BosConfig, databases, KeyFile/krb config, `run-tests.conf`, server directories, `/vicep<part>` volume data, PTS admin entries, VLDB entries, volumes, mount points, ACLs, and saved batch script when requested. On failure, the `END` block can run queued unwind commands.

## Dependencies And Integration Points
Integrates OS-specific service control, Kerberos/auth helpers, BOS/VOS/PTS/FS binaries, DNS, vice partitions, and the local cache manager. Later smoke tests assume the volumes and `/afs/<cell>/service` tree created here.

## Risks And Test Signals
The script is intentionally destructive and root-only. Quoting of saved shell options is simple and can be unsafe for unusual values. Sleeps assume startup timing. Unwind cannot guarantee complete rollback after partial server/database changes. Signals include successful `info: DONE`, running BOS/DB/file servers, created volumes, released RO paths, valid tokens, and passing follow-on ACL/BOS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afs-newcell.pl -->
