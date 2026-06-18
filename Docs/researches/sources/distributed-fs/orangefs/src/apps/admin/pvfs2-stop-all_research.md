<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-stop-all -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-stop-all

**Purpose:** `pvfs2-stop-all` is a bash cluster helper that kills `pvfs2-server` processes on every server derived from an OrangeFS config file.

**Important APIs, types, and functions:** The script uses GNU `getopt`, accepts config, exclusions, SSH options, and help, builds `SERVERS` from `Alias` lines with the same grep/tr/cut/sed pipeline as `pvfs2-start-all`, then runs `ssh $SERVER killall pvfs2-server`.

**Control flow:** It changes directory to its script directory, parses options, requires `-c`, builds and filters the server list, computes output spacing, and loops through servers. Empty SSH output is treated as a successful kill and printed as `pvfs2-server killed`.

**State and persistence:** It stops remote server processes and can make the filesystem unavailable. It does not remove data or edit config.

**Dependencies and integration points:** It depends on SSH, `killall`, config Alias syntax, and shell tools. It pairs with `pvfs2-start-all` for manual cluster lifecycle operations.

**Risks and edge cases:** `killall pvfs2-server` can affect every matching process on a host, including servers from other test clusters. Unquoted variables and parser fragility create command/splitting risks. Tests should use dry-run/mocked SSH, multiple alias forms, exclusions, hosts with no running server, and SSH failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-stop-all -->
