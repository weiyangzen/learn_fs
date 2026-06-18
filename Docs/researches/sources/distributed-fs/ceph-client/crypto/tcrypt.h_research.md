# sources/distributed-fs/ceph-client/crypto/tcrypt.h

`tcrypt.h` defines data structures and static speed-template data consumed by `tcrypt.c`. It centralizes key-size lists, a DES3 benchmark key, AEAD key-size lists, and generic hash block/update size matrices.

It defines `struct cipher_speed_template`, `struct aead_speed_template`, and `struct hash_speed`. It provides `DES3_SPEED_VECTORS`, `des3_speed_template[]`, multiple zero-terminated `speed_template_*` arrays, AEAD templates, and `generic_hash_speed_template[]`.

There is no runtime control flow and no owned mutable state. `tcrypt.c` iterates key-size arrays until a zero byte and hash speed arrays until `.blen == 0`. Integration is direct inclusion into the tcrypt module, where these templates determine benchmark coverage. Risks are template drift, accidental omission of key sizes, invalid key lengths for an algorithm mode, or buffer-size assumptions that no longer match `tcrypt.c`. Test signals include successful compilation, expected benchmark iteration counts, no buffer overflow warnings for largest templates, and visible logs for each generic hash speed entry.
