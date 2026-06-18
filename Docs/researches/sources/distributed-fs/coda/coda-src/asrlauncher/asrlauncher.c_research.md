# sources/distributed-fs/coda/coda-src/asrlauncher/asrlauncher.c

Purpose: Launches application-specific resolution commands for Venus conflicts using `.asr` rules files and a local allow-list policy.

Important APIs/functions: `escapeString`, `nameNextRulesFile`, `checkRulesFile`, `replaceEnvVars`, `executeTriggers`, `findRule`, `executeCommands`, and `main`. Global conflict state includes path, parent, basename, volume root, conflict type, policy path, and current rules file positions.

Control flow: Venus passes conflict path, volume root, conflict type, and policy file. Main derives basename/parent, escapes shell metacharacters in conflict paths, and calls `findRule`. Rule discovery walks up from conflict path to volume root, names each `.asr`, checks the local policy allow list, opens allowed rule files, and runs backtick-delimited trigger snippets until one exits 0. The matching rule's following command lines are then expanded and piped into `/bin/sh`, with timeout polling and failure reporting.

State and persistence: Reads local policy and `.asr` files. Does not directly write persistent state, but executed shell commands can mutate Coda-visible files. Global buffers carry conflict and rule-file state.

Dependencies and integration: Invoked by Venus. Depends on Coda compile-time `SYSTYPE`, standard fork/exec/wait/signal APIs, and shell execution. Environment-like variables include `$>`, `$<`, `$@`, `$=`, `$:`, and `$!` forms for conflict metadata.

Risks and test signals: This is security-sensitive. It executes rule-controlled shell snippets, so policy and escaping are critical. `escapeString` has a bug-like write to `str[maxlen - 1]` after copying into `tempstr`, and many `strncpy` calls may not NUL-terminate. `kill(pid * -1, SIGKILL)` intends process-group cleanup but the child is not placed into a new group here. Timeout loops use `select` polling. Allow-list path comparisons require careful normalization.
