# File Research: sources/block-storage/cryptsetup/lib/fvault2/fvault2.h

Declares the FileVault2 public-internal interface.

Key points:
- Defines fixed sizes for wrapped keys, PBKDF2 salt, and UUID strings.
- `struct fvault2_params` stores cipher/mode, key size, PBKDF2 parameters, wrapped KEK/VK material, UUIDs, logical volume offset, and logical volume size.
- Declares metadata read, volume-key derivation, dump, activation by volume key, and volume-key-size helper functions.

Storage relevance:
- This header is the contract between FileVault2 format handling and generic cryptsetup activation/keyslot code.
