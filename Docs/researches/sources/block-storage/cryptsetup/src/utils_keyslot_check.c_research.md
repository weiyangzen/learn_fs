# File Research: sources/block-storage/cryptsetup/src/utils_keyslot_check.c

## Purpose
Post-repair/randomness heuristic for detecting likely corrupted encrypted LUKS keyslot binary areas.

## Algorithm
- `bitcount()` manually counts set bits in 64-bit words.
- `chisquared_bytes()` computes a chi-squared statistic over byte frequency buckets.
- `chisquared_bits()` computes a chi-squared statistic over bit frequency buckets.
- `run_analysis()` scans keyslot data in 4096-byte blocks using a byte-distribution chi-squared threshold. Suspicious blocks are further scanned in 128-byte subblocks using a bit-distribution threshold.

## Public Entry
`luks_check_keyslots()`:
- Skips checks during reencryption.
- Opens the header/device read-only.
- Iterates active bound keyslots.
- Uses `crypt_keyslot_area()` and `crypt_keyslot_get_key_size()` to determine the actual encrypted keyslot data length.
- Reads the keyslot area and runs analysis.
- Prints up to three suspected offsets per keyslot and suggests a `hexdump` command if any suspicious offsets were found.

## Important Limits
- This is explicitly a hint, not proof of corruption.
- It skips inactive and unbound slots.
- It can produce false positives and cannot detect all corruption.
- It assumes encrypted keyslot material should look pseudorandom.

## Dependencies
Uses libcryptsetup keyslot metadata APIs plus common logging and `read_buffer`.
