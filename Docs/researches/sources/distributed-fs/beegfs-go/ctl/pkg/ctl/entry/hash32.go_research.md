# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/hash32.go

Purpose: implements the BeeGFS-compatible 32-bit hash used by entry toolkit path helpers.

Important APIs/types/functions: `hash32` and any helper constants/tables in the file.

Control flow: accepts a string and computes the deterministic uint32 checksum used by `getHashes` in `beegfstoolkit.go` to map entry IDs into metadata directory fanout paths.

State and persistence: pure computation.

Dependencies and integration points: consumed by `getHashes`, which feeds verbose dentry/inode path rendering. It must match the C++ BeeGFS hashing algorithm to produce correct paths.

Risks: any deviation from server/C++ hash behavior will produce wrong metadata paths. Signedness, byte order, and string-byte treatment are typical compatibility hazards for ported hash functions.

Test signals: no direct tests in this subset. Useful tests should compare known BeeGFS entry IDs to expected level-1/level-2 hash directories and raw hash values.
