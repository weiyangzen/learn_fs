# File Research: sources/block-storage/cryptsetup/src/cryptsetup_arg_list.h

## Purpose
Macro list defining every `cryptsetup` option. It is included multiple times with different `ARG(...)` definitions to generate enum IDs, `tools_arg` defaults, and popt option tables.

## Format
Each entry provides:
`long name, short name, popt type, help description, units, internal argument type, default value, allowed actions`.

## Main Option Groups
- General behavior: batch mode, verbose, debug, debug JSON, test args, timeout, disable locks, disable blkid.
- Device activation: type, readonly, allow discards, persistent flags, refresh, shared, size/device-size, offset/skip, sector size, IV large sectors, dm-crypt performance flags.
- Key input: key file, keyfile offset/size, key size, key slot, volume-key file/keyring, key descriptions, keyring linking.
- LUKS formatting/config: cipher, hash, UUID, label, subsystem, metadata/keyslot sizes, PBKDF selection/costs, RNG selection, force password, integrity options.
- Reencryption: encrypt/decrypt/init/resume modes, active name, hotzone, resilience, block size, direct I/O, fsync, write log, reduce device size, keep/new key options.
- Token handling: token ID/type/only/replace, new token ID, JSON file.
- TCRYPT/VeraCrypt: hidden/system/backup headers, VeraCrypt enable/disable, PIM and query-PIM.
- OPAL: `--hw-opal`, `--hw-opal-only`, `--disable-sum`, factory reset.
- Compatibility aliases: `--new`, `--dump-master-key`, `--master-key-file`.

## Defaults And Aliases
- Some options use libcryptsetup sentinel defaults such as `CRYPT_ANY_SLOT` and `CRYPT_ANY_TOKEN`.
- PBKDF memory and parallelism default from LUKS2 build defaults.
- Alias entries use `CRYPT_ARG_ALIAS` to redirect parsing into the canonical option.

## Notes
- This file deliberately contains no enum or array syntax outside the macro calls.
- Action allowlists are defined in `cryptsetup_args.h`; empty action arrays mean globally allowed.
