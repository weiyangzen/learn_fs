# sources/distributed-fs/coda/coda-src/scripts/vice-setup.in

Purpose: top-level interactive Coda server setup script for SCM and non-SCM servers.

Control flow: rejects arguments, determines hostname/domain, removes existing `server.conf` after confirmation, locates `server.conf.ex`, prompts for `vicedir`, writes baseline config (`vicedir`, `rvmtruncate`, `trace`), creates standard subdirectories, asks whether this host is SCM. Non-SCM setup writes SCM hostname and update token, fetches required db files from SCM with `updatefetch`, and later runs RVM and srvdir setup. SCM setup prompts for update/auth2/volutil tokens, creates update file lists, touches empty DB placeholders, writes hostname, configures `codatunnel`, runs SCM/user/RVM/srvdir sub-scripts, optionally starts daemons, and optionally creates root volume `/`.

State/persistence: creates server config/tree, token files, update file lists, authentication/protection DBs, RVM areas, server directory, SCM metadata, and optionally starts services/creates root volume.

Dependencies, risks, tests: depends on many generated scripts and daemons (`codaconfedit`, `updatefetch`, `vice-setup-*`, `auth2`, `updatesrv`, `updateclnt`, `startserver`, `createvol_rep`). Risks include highly interactive destructive flow, token handling on terminal, partial setup across many files, direct `/etc/rc.local` edits on BSD, and no transaction/rollback. Test SCM and non-SCM paths in a sandboxed `vicedir`, failed SCM fetch, codatunnel config, sub-script failure propagation, and optional startup/root volume creation.
