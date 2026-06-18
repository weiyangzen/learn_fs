# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_key.py

## Role

Defines parser command specifications for key operations.

## Commands

- `set`: set a key in the kernel keyring.
- `reset`: reset an existing key.
- `unset`: remove a key.
- `list`: list Stratis keys.

## Parser Behavior

`set` and `reset` use a mutually exclusive key-value source group from `KEYFILE_PATH_OR_STDIN`, allowing keyfile or stdin-based key input.

## Dependencies

Maps commands to `TopActions` methods and shared keyfile/stdin argument definitions.

## Notable Risk Areas

These parser choices feed passphrase/file-descriptor handling in `_actions/_top.py` and `_actions/_utils.py`, so argument names must stay aligned.
