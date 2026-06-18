<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/autocomplete/ctr -->
# sources/cloud-native/containerd/contrib/autocomplete/ctr

## Purpose
Bash completion shim for the `ctr` CLI.

## Important APIs, Types, And Functions
Defines `_cli_bash_autocomplete` and registers it with `complete`.

## Control Flow
When completing, invokes the current ctr command prefix with `--generate-bash-completion`, then feeds options into `compgen`.

## State And Persistence
Shell-session only; no files written.

## Dependencies And Integration Points
bash completion, ctr binary support for urfave/cli completion.

## Risks And Test Signals
Executes partially typed command words; quoting/word-splitting is simple. Manual shell test signal. Source size reviewed: 22 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/autocomplete/ctr -->
