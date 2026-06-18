# File Research: sources/block-storage/cryptsetup/src/veritysetup_args.h

This header defines the argument metadata infrastructure for `veritysetup`.

Key contents:
- Include guard `VERITYSETUP_ARGS_H`.
- Includes shared argument name and macro helpers.
- Defines action name constants: `close`, `dump`, `format`, `open`, `status`, and `verify`.
- Defines per-option action allowlists used by `veritysetup_arg_list.h`.
- Generates option enum IDs from `veritysetup_arg_list.h`.
- Generates the global `tool_core_args[]` table from the same X-macro list.

Action allowlists:
- `--deferred` applies to `close`.
- Corruption behavior options apply to `open`.
- `--root-hash-file` applies to `format`, `open`, and `verify`.
- `--root-hash-signature`, `--use-tasklets`, and `--shared` apply to `open`.

Generated structures:
- The enum starts with `OPT_UNUSED_ID = 0`, then appends one `_ID` per option.
- `tool_core_args[]` begins with an unused placeholder, then one `struct tools_arg` per option with name, set flag, internal type, default value, and allowed actions.

Design role:
- Keeps `veritysetup.c` small by centralizing action names, option IDs, default values, and action restrictions.
- Shares the same declarative option source with POPT table generation, reducing drift between parsing, validation, and internal option lookup.
