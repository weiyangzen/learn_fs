# sources/distributed-fs/ceph-client/tools/perf/perf-completion.sh

### Purpose
This script provides Bash and Zsh completion for perf commands, options, subcommands, event names, PMU events, and metric names.

### Important APIs, Types, And Functions
Compatibility helpers `__my_reassemble_comp_words_by_ref()`, `__perf_get_comp_words_by_ref()`, and `__perf__ltrim_colon_completions()` replace missing bash-completion functions. `__perfcomp()` and `__perfcomp_colon()` generate completions. `__perf_prev_skip_opts()` identifies the active perf subcommand. `__perf_main()` contains the completion decision tree. Shell-specific `_perf()` functions register completion for Zsh or Bash.

### Control Flow
The script first detects whether helper functions are preloaded. Completion determines the current word, finds the nearest command context, then completes top-level commands/options, event names after `-e/--event`, `--pfm-events`, stat metrics after `-M/--metrics`, nested subcommands, or long options. It queries perf dynamically via `--list-cmds`, `--list-opts`, and `perf list --raw-dump`.

### State And Persistence
It mutates shell completion variables such as `COMPREPLY`, `COMP_WORDBREAKS`, and Zsh `_ret`. No files are written.

### Dependencies And Integration Points
It integrates with Bash programmable completion, Zsh `compdef`, the installed `perf` executable, `/sys/bus/event_source/devices/cpu/events`, and shell pattern matching.

### Risks
Dynamic calls to `perf list` and sysfs can be slow or unavailable. Some expansions intentionally split on spaces and assume event names are completion-safe. Architecture-specific sysfs checks special-case aarch64 only.

### Test Signals
Source the script in Bash and Zsh and test top-level command completion, `perf record -e`, comma-separated events, `perf stat -M`, long options, and nested commands like `perf script`.
