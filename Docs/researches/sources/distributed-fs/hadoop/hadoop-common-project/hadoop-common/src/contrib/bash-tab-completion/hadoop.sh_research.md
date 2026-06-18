# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/contrib/bash-tab-completion/hadoop.sh

Purpose: Bash completion script for the top-level `hadoop` command. It executes and parses the installed Hadoop script to complete subcommands, command options, JAR/local paths, and HDFS paths. The source was read as a complete 119-line file.

Important APIs/functions: defines `_hadoop` and registers it with `complete -F _hadoop hadoop`. Uses Bash completion globals `COMP_WORDS`, `COMP_CWORD`, and `COMPREPLY`, plus `compgen`, `which`, `grep`, `awk`, `cut`, `sort`, and Hadoop command output.

Control flow: completion first resolves the executable for the current command and exits unless it is an executable file. For the first argument it parses the usage output before the `or` usage line and extracts leading command names. For the second argument it has command-specific parsers for `dfs`, `dfsadmin`, `fs`, `job`, `pipes`, `jar`, and `namenode`. For later arguments, it infers parameter names for `dfs`/`fs` subcommands and completes HDFS paths via `-ls -d` or local filesystem paths via `compgen -A file`.

State and persistence: all state is shell-local and transient in `COMPREPLY`. It does not write files or cache completions.

Dependencies and integration: depends on the installed `hadoop` shell launcher and the stability of usage/help output from Hadoop commands. It integrates with Bash completion infrastructure on systems that source scripts from `/etc/bash_completion.d/`.

Risks: completion executes the target script repeatedly, so slow or side-effectful command help paths affect interactive shells. Several expansions are unquoted, command output parsing is fragile, and only a subset of subcommands receives deep argument completion. HDFS path completion depends on the active cluster and user credentials.

Test signals: manual tab-completion checks for first-level commands, option completion for `fs` and `dfsadmin`, local JAR path completion, HDFS path completion against a test cluster, and shellcheck/BATS coverage for quoting regressions where feasible.
