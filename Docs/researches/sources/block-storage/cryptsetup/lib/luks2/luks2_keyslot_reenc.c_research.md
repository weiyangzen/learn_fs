# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_reenc.c

Concrete handler and helper layer for `reencrypt` keyslots, which store online reencryption resilience metadata rather than passphrase-unlocked volume keys. It allocates and validates reencryption keyslot JSON, writes reencryption metadata to the binary area, dumps resilience settings, loads protection descriptors, and supports controlled resilience-mode updates.

Key responsibilities:
- Provides a handler whose `open` always returns `-ENOENT`, because reencryption keyslots are not passphrase unlock slots.
- Builds the keyslot `area` JSON for resilience modes: `checksum`, `journal`, `none`, `datashift`, `datashift-checksum`, and `datashift-journal`.
- Allocates a reencryption keyslot with type, dummy `key_size = 1`, reencrypt mode, direction, and area metadata.
- Chooses storage area by finding a maximum gap for most resilience modes and only a minimal area for plain datashift, which does not require extra stored protection data.
- Stores reencryption data into the keyslot area using locked raw block writes.
- Wipes reencryption verification references from digests.
- Dumps mode, direction, resilience type, hash/sector size or shift size where applicable, and area offset/length.
- Validates reencryption keyslot JSON: legal mode, legal direction, key size exactly 1, checksum fields and power-of-two sector size, datashift shift-size presence and 512-byte alignment.
- Detects whether an existing reencryption keyslot needs update based on requested resilience, hash, checksum block size, and data-shift size.
- Loads primary and secondary resilience descriptors into `struct reenc_protection`, including checksum hash context initialization.
- Restricts updates so callers cannot switch to or away from datashift categories or change datashift size.
- Updates area JSON transactionally: keeps a reference to the old area, installs the new one, validates, and restores the old area if validation fails.
- Public helpers allocate, test update need, perform updates, refresh reencryption verification digest, validate hotzone capacity for secondary protection, write the header, and load resilience data.

Important behavior:
- Reencryption keyslots must have priority set to `CRYPT_SLOT_PRIORITY_IGNORE` after allocation so normal unlock attempts skip them.
- Allocation checks JSON size after inserting the keyslot and removes it if the metadata area cannot hold the new object.
- Checksum resilience records both `hash` and `sector_size`; datashift variants additionally record `shift_size` in bytes.
- Updating checksum block size without changing resilience uses a copy of the existing area with only `sector_size` changed.
- Before updating resilience metadata, the code verifies the existing reencryption digest against supplied volume keys.
- If the new secondary protection type needs storage, it computes the maximum hotzone size and refuses updates when the moved segment requires more protection space than the new type provides.
- The handler table exposes `store`, `wipe`, `dump`, and `validate`, but public allocation/update/load helpers are separate from the generic keyslot store path.

Dependencies:
- Depends on `luks2_internal.h` for header access, JSON helpers, area finding, metadata locks/writes, digest assignment, reencryption digest verification/creation, hotzone sizing, and protection cleanup.
- Uses cryptsetup block I/O helpers (`device_open_locked`, `write_lseek_blockwise`, block size/alignment helpers) for raw metadata writes.
- Uses crypt hash APIs to initialize checksum resilience state.
- Uses `crypt_params_reencrypt`, `crypt_reencrypt_mode_to_str()`, and reencryption direction/mode constants.

Notable risks:
- The validation branch for datashift-related types is structured so `datashift-checksum` is consumed by the checksum branch first; the separate datashift branch handles plain datashift and datashift-journal. This matches stored fields created by allocation but is easy to misread when extending validation.
- Reencryption resilience updates are intentionally constrained; loosening datashift category or shift-size immutability could break crash-recovery assumptions.
- Raw writes to the reencryption area depend on buffer length fitting inside the configured area and on external device locking.
- The `open` method is a sentinel; callers must not expect reencryption keyslots to produce volume keys through the normal keyslot unlock path.
