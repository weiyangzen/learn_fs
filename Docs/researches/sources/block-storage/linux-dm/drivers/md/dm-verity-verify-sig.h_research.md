# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.h

## Purpose
Declares dm-verity root-hash signature verification constants, temporary option storage, and enabled/disabled build interfaces.

## Main Interfaces
- Defines `DM_VERITY_ROOT_HASH_VERIFICATION` and the option name `root_hash_sig_key_desc`.
- Defines `struct dm_verity_sig_opts` with signature size and signature bytes.
- When enabled, declares root-hash verification, signature option recognition/parsing, and option cleanup.
- When disabled, provides no-op or rejecting stubs and sets signature option count to zero.

## Control Flow
The header only selects real declarations or stubs through `CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG`. Disabled builds make root-hash verification always succeed and make signature option parsing unavailable.

## State And Synchronization
No runtime state is owned by this header. Temporary signature memory is described by `struct dm_verity_sig_opts` and owned by constructor parsing code.

## Integration Points
Included by the verity target and signature implementation. The option count feeds into dm-verity's maximum optional argument calculation.

## Notable Behaviors
- Enabled builds reserve two optional table arguments: option name plus key descriptor.
- Disabled builds reject the signature option as unrecognized via the parser path.

## Risks And Review Focus
- Option count must remain consistent with the parser consuming exactly one value after the option name.
- Stub behavior means table compatibility differs across kernel configurations.
