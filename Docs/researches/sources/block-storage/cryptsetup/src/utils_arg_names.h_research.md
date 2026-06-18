# File Research: sources/block-storage/cryptsetup/src/utils_arg_names.h

## Purpose
Central list of long command-line option names used by cryptsetup, integritysetup, veritysetup, and related utilities.

## Contents
Defines `OPT_*` string macros for:
- Cryptsetup/LUKS options: cipher, hash, header, UUID, key file, keyslot, PBKDF, labels, tokens, OPAL, reencryption, performance flags.
- Integritysetup options: journal, bitmap, tag size, integrity key, no-wipe/wipe, recalculate, inline mode.
- Verity-related options also present in the shared namespace: FEC, root hash, salt, corruption handling, data/hash block sizing.
- Compatibility aliases: master key names, new, etc.

## Design Role
This header avoids string duplication between option-list files and any code that needs stable option names for diagnostics.

## Notes
Several macros are not used by the files in this group directly because the name namespace spans multiple cryptsetup utilities.
