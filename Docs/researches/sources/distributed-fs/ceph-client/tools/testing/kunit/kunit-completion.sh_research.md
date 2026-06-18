# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit-completion.sh

## Purpose

This shell script provides bash completion for the KUnit command-line tool. It completes top-level subcommands and option flags by asking the local `kunit.py` script for hidden `--list-cmds` and `--list-opts` output.

## Important APIs, Types, And Data

It defines `_kunit_dir` from `${BASH_SOURCE[0]}` and a completion function `_kunit()`. It uses bash-completion's `_init_completion` to populate `cur`, `prev`, `words`, and `cword`. It invokes `${_kunit_dir}/kunit.py --list-cmds`, `${script} ${words[1]} --list-opts`, or `${script} --list-opts`, then fills `COMPREPLY` via `compgen -W`. It registers completions for `kunit.py`, `kunit`, and `./tools/testing/kunit/kunit.py`.

## Control Flow

On completion, `_kunit()` initializes completion state. If completing the first non-option word, it lists subcommands. If completing an option after a subcommand, it lists options for that subcommand; otherwise it lists root options. Non-option arguments beyond the command are left to bash's default completion because the function returns without setting `COMPREPLY`.

## State And Persistence Behavior

The script has no persistent state. Runtime state is limited to shell variables and `COMPREPLY`. It depends on the current checkout's `kunit.py` output each time completion runs, so option lists track parser changes without manual duplication.

## Dependencies And Integration Points

It depends on bash, bash-completion's `_init_completion`, executable Python `kunit.py`, and `kunit.py`'s hidden `--list-cmds`/`--list-opts` behavior. It integrates with shells that source this file and commands named `kunit.py`, `kunit`, or the relative tool path.

## Risks And Edge Cases

If bash-completion is not installed, `_init_completion` is missing and the function silently returns. The script does not quote `${words[1]}` in the command invocation, but subcommands are parser-defined simple words. Completion can be slow if `kunit.py` startup is slow. Errors from `kunit.py` are discarded, so broken parsers produce empty completions.

## Test Signals

Source the script in bash and run `complete -p kunit.py`. `COMP_WORDS`-driven manual tests or interactive tab completion should show `run config build exec parse` at the command position and appropriate parser options after a subcommand.
