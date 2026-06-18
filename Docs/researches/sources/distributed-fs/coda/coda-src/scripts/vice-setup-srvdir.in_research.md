# sources/distributed-fs/coda/coda-src/scripts/vice-setup-srvdir.in

Purpose: interactive setup for the server container-file hierarchy and `vicetab` entry.

Control flow: loads `server.conf`, determines hostname, explains storage directory requirements, prompts for a server data directory defaulting to `/vicepa`, creates it if absent and rejects existing `FTREEDB`, touches `FTREEDB`, asks whether to add a `vicetab` entry, rejects duplicates, prompts for capacity class (`256K`, `1M`, `2M`, `16M`), and appends a matching `ftree width/depth` line with hostname and directory.

State/persistence: creates data directory, creates `FTREEDB`, and appends to `$vicedir/db/vicetab`.

Dependencies, risks, tests: depends on config, hostname, interactive shell, and ftree layout assumptions. Risks include no rollback if `vicetab` append fails after `FTREEDB`, simple `grep "$srvdir"` duplicate detection, symlink acceptance, and only four preset size classes. Test existing FTREEDB rejection, symlink data dir, each size option, duplicate vicetab entry, and no-vicetab path.
