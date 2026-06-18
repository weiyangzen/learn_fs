# File Research: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.h

## Purpose

`tcrypt.h` declares the internal TCRYPT/VeraCrypt header layout, constants, forward declarations, and function interface used by `setup.c` and `tcrypt.c`.

## Constants

- Header sizing:
  - `TCRYPT_HDR_SALT_LEN` is 64 bytes.
  - `TCRYPT_HDR_IV_LEN` is 16 bytes.
  - `TCRYPT_HDR_LEN` is 448 encrypted-header bytes.
  - `TCRYPT_HDR_KEY_LEN` is 192 bytes of derived header key material.
  - `TCRYPT_HDR_MAGIC_LEN` is 4 bytes.
- Magic values:
  - `TCRYPT_HDR_MAGIC` is `"TRUE"`.
  - `VCRYPT_HDR_MAGIC` is `"VERA"`.
- Header offsets:
  - old hidden header offset: `-1536`;
  - current hidden header offset: `65536`;
  - hidden backup offset: `-65536`;
  - normal backup offset: `-131072`;
  - system header offset: `31744`.
- Key material:
  - `TCRYPT_LRW_IKEY_LEN` is 16 bytes.
  - TrueCrypt keyfile/passphrase pool length is 64 bytes.
  - VeraCrypt pool length is 128 bytes.
  - keyfile read cap is 1 MiB.
- Header flags define system and nonsystem volume bits.

## Header Layout

- `struct tcrypt_phdr` is packed and exactly 512 bytes in practice: 64-byte salt followed by a 448-byte encrypted/plain union.
- The decrypted header view contains:
  - 4-byte magic;
  - TCRYPT and required-driver versions;
  - CRC32 of key area;
  - reserved timestamp fields;
  - hidden volume size and visible volume size;
  - master-key offset and size;
  - flags and sector size;
  - reserved bytes;
  - header CRC32;
  - 256-byte encrypted-volume key pool.
- Multi-byte on-disk fields are stored big-endian and converted by `TCRYPT_hdr_from_disk()` in `tcrypt.c`.

## Interface

The header exposes internal TCRYPT operations:

- `TCRYPT_read_phdr()` reads and decrypts a TCRYPT/VeraCrypt header using `crypt_params_tcrypt`.
- `TCRYPT_init_by_name()` reconstructs TCRYPT parameters/header state from an active dm mapping.
- `TCRYPT_activate()` creates the required dm-crypt mapping chain.
- `TCRYPT_deactivate()` removes the public mapping and private subdevices.
- `TCRYPT_get_data_offset()` and `TCRYPT_get_iv_offset()` compute dm offsets for normal, hidden, legacy, and system layouts.
- `TCRYPT_get_volume_key()` exports reconstructed volume key material.
- `TCRYPT_dump()` prints decoded TCRYPT/VeraCrypt metadata.

## Dependencies

The file forward-declares `crypt_device`, `crypt_params_tcrypt`, `dm_target`, `volume_key`, and `device`, keeping the TCRYPT interface internal and avoiding heavy includes beyond `<stdint.h>`.
