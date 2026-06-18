# sources/cloud-native/cri-o/internal/criocli/completion.go

Purpose: implements shell completion generation for bash, fish, and zsh.

Important APIs/types/functions: `completion`, `bashCompletion`, `zshCompletion`, `zshQuoteCmd`, and `fishCompletion`; templates `bashCompletionTemplate` and `zshCompletionTemplate`.

Control flow: the command defaults to bash when no shell argument is given, requires exactly one shell argument otherwise, and dispatches to the selected generator. Bash and zsh generation iterate visible commands and global flags, skipping hidden commands. Zsh command entries are quoted with single quotes unless usage contains a single quote, in which case double quotes are used and `$` is escaped. Fish delegates to `c.App.ToFishCompletion`.

State and persistence behavior: writes generated completion script to `c.App.Writer`; no persistent files.

Dependencies/integration points: urfave/cli. `DefaultCommands` includes this command for CRI-O binaries.

Risks: generated bash completion is simple and only completes top-level commands/global flags. Zsh quoting covers `$` only in double-quoted fallback and may need expansion if usage strings contain other shell metacharacters.

Test signals: `criocli_test.go` covers `zshQuoteCmd` through the test-only export in `completion_test.go`.
