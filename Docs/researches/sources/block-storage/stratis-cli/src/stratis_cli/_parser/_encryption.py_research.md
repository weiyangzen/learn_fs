# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_encryption.py

## Role

Defines parser command specifications for pool encryption, binding, rebind, and unbind commands.

## Main Components

- `ClevisEncryptionOptionsForTang` and `ClevisEncryptionOptionsForTpm2` specialize shared Clevis option parsing.
- `BIND_SUBCMDS` and `REBIND_SUBCMDS` define legacy `pool bind` / `pool rebind` forms.
- `BIND_SUBCMDS_ENCRYPTION` and `REBIND_SUBCMDS_ENCRYPTION` define newer `pool encryption bind` / `rebind` forms.
- `ENCRYPTION_SUBCMDS` defines `on`, `off`, `reencrypt`, `bind`, `rebind`, and `unbind`.

## Parser Behavior

Uses post-parser classes, mutually exclusive UUID/name groups, Tang trust URL/thumbprint groups, token-slot validation through `ensure_nat`, and explicit `IN_PLACE` arguments for state-changing encryption transitions.

## Dependencies

Imports `BindActions`, `CryptActions`, `RebindActions`, `Clevis`, `EncryptionMethod`, and shared parser helpers.

## Notable Risk Areas

This file carries command migration behavior through `MoveNotice` epilog text. It also maps several user-facing command variants to the same action methods, so namespace compatibility matters.
