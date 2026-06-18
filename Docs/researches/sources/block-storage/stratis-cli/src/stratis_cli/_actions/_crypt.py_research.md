# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_crypt.py

## Role

Implements pool encryption state transitions: encrypt an existing pool, decrypt an encrypted pool, and reencrypt with a new master key.

## Main Behavior

- `CryptActions.encrypt()` requires explicit `--in-place`, rejects already encrypted pools, builds optional Clevis/keyring arguments, and calls `Pool.Methods.EncryptPool`.
- `CryptActions.unencrypt()` requires explicit `--in-place`, rejects already unencrypted pools, and calls `Pool.Methods.DecryptPool`.
- `CryptActions.reencrypt()` requires explicit `--in-place` and calls `Pool.Methods.ReencryptPool`.

## Safety Checks

The explicit in-place requirement is enforced with `StratisCliInPlaceNotSpecified`. After daemon success, methods re-read or inspect pool state and raise `StratisCliIncoherenceError` if stratisd reports success without the expected state transition.

## Error Handling

- Already-in-target-state cases become `StratisCliNoChangeError`.
- Nonzero daemon return codes become `StratisCliEngineError`.
- Some expected “already encrypted” conditions are mapped via `StratisdErrors`.

## Notable Risk Areas

These are destructive or high-impact operations, so correctness depends on parser enforcement, explicit user opt-in, daemon-side result flags, and postcondition checks all remaining aligned.
