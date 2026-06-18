# File Research: sources/block-storage/cryptsetup/lib/luks1/af.h

This header declares LUKS1 anti-forensic splitter and keyslot storage encryption helpers.

Declared APIs:
- `AF_split`: split one block of key material into anti-forensic stripes.
- `AF_merge`: recover original key material from stripes.
- `AF_split_sectors`: compute sector-rounded storage size for split data.
- `LUKS_encrypt_to_storage`: encrypt keyslot data to the metadata device.
- `LUKS_decrypt_from_storage`: decrypt keyslot data from the metadata device.

Filesystem/block-storage relevance:
- These functions are central to LUKS1 keyslot storage: anti-forensic striping plus encrypted reads/writes to sectors on the metadata device.
