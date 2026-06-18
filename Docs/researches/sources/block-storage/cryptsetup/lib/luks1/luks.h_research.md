# File Research: sources/block-storage/cryptsetup/lib/luks1/luks.h

Defines the LUKS1 on-disk header ABI and declares the LUKS1 management API implemented primarily by `keymanage.c`.

Key definitions:
- Fixed string sizes for cipher name, cipher mode, hash spec, UUID, salts, and digest.
- `LUKS_NUMKEYS` is 8; `LUKS_STRIPES` is 4000.
- Keyslot active markers include old and current constants; current enabled marker is `0x00AC71F3`, disabled marker is `0x0000DEAD`.
- Header magic is `{'L','U','K','S',0xba,0xbe}` and version is handled by code as version 1.
- `LUKS_ALIGN_KEYSLOTS` is 4096 bytes; `LUKS_MAX_KEYSLOT_SIZE` is 16 MiB for wipe safety.

Main structure:
- `struct luks_phdr` is the packed conceptual LUKS1 metadata layout: magic/version, cipher/hash fields, payload offset, master key size, master-key digest/salt/iterations, UUID, 8 keyblock entries, and padding to sector alignment.
- Each keyblock stores active state, PBKDF iteration count, salt, key material offset, and AF stripe count.
- Comment states integer values are stored in network byte order on disk.

Declared API:
- Header generation/read/write/backup/restore/UUID update.
- Keyslot set/open/delete/wipe/info/count/area/PBKDF helpers.
- Volume-key verification and LUKS1 activation.

Role in the subsystem:
- This header is the compatibility boundary for LUKS1 code and for conversion paths referenced by LUKS2 headers.
