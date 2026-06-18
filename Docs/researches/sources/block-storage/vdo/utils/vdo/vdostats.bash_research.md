# File Research: sources/block-storage/vdo/utils/vdo/vdostats.bash

## Purpose

`vdostats.bash` provides Bash completion for the `vdostats` command.

## Behavior

It defines `_vdostats()`:

1. Calls `_init_completion`.
2. Clears `COMPREPLY`.
3. Defines possible options:
   - `--help`
   - `--all`
   - `--human-readable`
   - `--si`
   - `--verbose`
   - `--version`
4. Uses `compgen -W` against the current word to populate completions.

It registers completion with:

```bash
complete -F _vdostats vdostats
```

## Dependencies

This completion assumes the standard Bash completion environment where `_init_completion` is available.

## Notable Behaviors and Risks

- The TODO notes that device-name completion is not implemented.
- Only long options are completed, even though `vdostats` also supports short options.
