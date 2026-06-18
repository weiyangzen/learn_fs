# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_json_format.c

Implements LUKS2 JSON metadata formatting, keyslot-area allocation helpers, header generation, wipe behavior, and storage-size parameter calculation.

Area allocation:
- Keyslot material size is currently `keylength * 4000` rounded to 4096, mirroring AF split sizing.
- Keyslot areas live after both metadata copies: minimum offset is `2 * hdr->hdr_size`.
- Maximum usable metadata/keyslot area is `LUKS2_hdr_and_areas_size(hdr)`.
- `LUKS2_find_area_gap()` finds the first aligned gap large enough for a keyslot.
- `LUKS2_find_area_max_gap()` finds the largest free gap, adding a sentinel at the current max offset.
- Both functions scan all possible LUKS2 keyslots, sort existing allocated areas by offset, and avoid overlap.

Sizing validation:
- `LUKS2_check_metadata_area_size()` accepts only supported metadata sizes matching known secondary-header offsets.
- `LUKS2_check_keyslots_area_size()` rejects misaligned or too-large keyslot areas.

Header generation:
- `LUKS2_generate_hdr()` initializes header version, sequence ID, checksum algorithm, salts, UUID, top-level JSON objects (`keyslots`, `tokens`, `segments`, `digests`, `config`), creates a PBKDF2 digest, assigns it to segment 0, and creates the initial segment.
- Supports three segment modes: normal dm-crypt, OPAL-only, and OPAL+dm-crypt.
- Stores `json_size` and `keyslots_size` in config.
- Warns when the keyslot area is so small that available keyslot count is limited.

Wipe behavior:
- `LUKS2_wipe_header_areas()` validates metadata, bounds the zero wipe to metadata/keyslot maxima and device size, wipes metadata area with zeroes, ensures actual header/keyslot area exists, then wipes keyslot area with random data if configured.

Storage parameter calculation:
- `LUKS2_hdr_get_storage_params()` derives metadata size, keyslots size, and data offset from crypt device settings and alignment constraints.
- Metadata defaults to 16 KiB when unspecified.
- Keyslots size is inferred from explicit data offset when possible, capped at 128 MiB, 4 KiB aligned, and reduced if the metadata device is too small.
- Data offset has priority; otherwise it is aligned after two metadata areas plus keyslots area.

Role:
- This file builds the initial logical LUKS2 JSON layout and decides where variable-sized keyslot areas fit inside the metadata/keyslots region.
