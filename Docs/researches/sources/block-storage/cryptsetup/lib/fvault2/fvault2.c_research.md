# File Research: sources/block-storage/cryptsetup/lib/fvault2/fvault2.c

Implements FileVault2/CoreStorage-compatible metadata reading, volume-key derivation, dumping, and activation.

Key points:
- Defines packed CoreStorage structures for the volume header, metadata block headers, XML-bearing metadata block types, volume group descriptor, passphrase-wrapped KEK, and KEK-wrapped volume key.
- `_check_crc()` validates CoreStorage CRC32C checksums with required seed `0xffffffff`.
- `_unwrap_key()` implements AES key unwrap for 128-bit KEKs and wrapped keys using AES-ECB decrypt, validating the `0xA6...A6` integrity value.
- `_search_xml()` uses regex over XML plist strings to extract keyed values.
- Metadata block `0x0019` parser extracts PBKDF2 salt/iteration count, wrapped KEK, and wrapped volume key from base64 XML data.
- Metadata block `0x001A` parser extracts logical volume size and family UUID.
- Metadata block `0x0305` parser extracts logical volume block offset.
- `_read_volume_header()` reads and validates the physical volume header, CoreStorage magic, version, AES key size, and builds the encrypted-metadata XTS key from header key data plus physical-volume UUID.
- `_read_disklabel()` finds encrypted metadata block offset/count through the disk label metadata block and volume group descriptor.
- `_read_encrypted_metadata()` decrypts encrypted metadata blocks with AES-XTS, validates CRCs, and requires all three relevant metadata types.
- `FVAULT2_read_metadata()` orchestrates header, disk label, and encrypted metadata reads, then fixes cipher parameters to `aes` and `xts-plain64`.
- `FVAULT2_get_volume_key()` derives a passphrase key with PBKDF2-HMAC-SHA256, unwraps KEK and volume key, then derives the second XTS half by SHA256(volume-key-half || family-uuid).
- Activation builds a dm-crypt target over the logical volume offset/size with the derived AES-XTS key.
- Sensitive temporary keys use safe allocation/free where relevant.

Storage relevance:
- Adds read/activate support for FileVault2 volumes within cryptsetup’s block-storage toolchain.
- Relies on crypto backend PBKDF2, hash, and AES ECB/XTS support.
