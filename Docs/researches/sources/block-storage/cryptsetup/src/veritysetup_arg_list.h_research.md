# File Research: sources/block-storage/cryptsetup/src/veritysetup_arg_list.h

This header is an X-macro list of all `veritysetup` command-line options. It is included multiple times with different `ARG(...)` definitions to generate POPT options, enum IDs, and `struct tools_arg` metadata.

Each entry provides:
- Long option name.
- Short option character, if any.
- POPT argument type.
- Help text.
- Unit/help suffix.
- Internal argument type.
- Default value.
- Allowed actions list, where empty means global.

Defined options:
- Deferred close controls: `--deferred`, `--cancel-deferred`.
- Verification behavior: `--ignore-corruption`, `--restart-on-corruption`, `--panic-on-corruption`, `--error-as-corruption`, `--ignore-zero-blocks`, `--check-at-most-once`, `--use-tasklets`.
- Format/load parameters: `--data-block-size`, `--data-blocks`, `--hash-block-size`, `--hash-offset`, `--hash`, `--format`, `--salt`, `--uuid`, `--no-superblock`.
- FEC parameters: `--fec-device`, `--fec-offset`, `--fec-roots`.
- Root hash inputs/outputs: `--root-hash-file`, `--root-hash-signature`.
- Activation sharing: `--shared`.
- Common output controls: `--debug`, `--verbose`.

Defaults encoded here:
- Data block size defaults to `DEFAULT_VERITY_DATA_BLOCK`.
- Hash block size defaults to `DEFAULT_VERITY_HASH_BLOCK`.
- FEC roots defaults to `DEFAULT_VERITY_FEC_ROOTS`.
- Format defaults to `1`.
- Hash defaults to `DEFAULT_VERITY_HASH`.

Notable design:
- Action restrictions are symbolic macros from `veritysetup_args.h`, so invalid option/action combinations can be caught centrally by `tools_check_args()`.
- The list is intentionally declarative and contains no executable logic.
