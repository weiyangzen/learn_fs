<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-start-all -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-start-all

**Purpose:** `pvfs2-start-all` is a bash cluster helper that starts all `pvfs2-server` processes named by `Alias` lines in an OrangeFS config file over SSH, then optionally pings the mounted filesystem.

**Important APIs, types, and functions:** The script uses GNU `getopt`, parses `--conf`, `--prefix`, optional exclusions, mount, SSH options, server options, and server environment. It derives `SERVERS` by grepping `Alias` lines, splitting on spaces/commas, extracting host portions after `:`, and stripping `/`. It runs `$PREFIX_PATH/sbin/pvfs2-server` remotely through `ssh`.

**Control flow:** It changes directory to the install root relative to the script, parses options, requires config and prefix, builds the server list, applies exclusion filters, computes display spacing, starts each server with SSH, sleeps three seconds, then optionally invokes `bin/pvfs2-ping -m $MNT`.

**State and persistence:** It starts remote server processes and can alter cluster availability. It does not persist config, but it relies on server options/environment for runtime behavior.

**Dependencies and integration points:** It depends on shell, GNU getopt, SSH reachability, config file syntax, prefix layout, `pvfs2-server`, and optionally `pvfs2-ping`.

**Risks and edge cases:** Config parsing is grep/tr/sed based and can mis-handle unusual Alias syntax. Several variables are unquoted in command substitutions and SSH invocation, so spaces and shell metacharacters are risky. The long-option spec appears to miss a comma between `server_options:` and `server_env:`. Tests should use sample configs with multiple aliases, exclusions, SSH option strings, env strings, failed remote starts, and optional ping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-start-all -->
