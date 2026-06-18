## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib-hashes.sh

Purpose: centralizes stable CID/hash constants used by sharness scripts.

Important content: defines common known hashes such as the empty-directory CID or canonical fixture CIDs before `test-lib.sh` sources sharness. There is no control flow beyond shell variable assignment and no persistence.

Dependencies and integration points: sourced early by `lib/test-lib.sh`, making constants globally available to command tests. Many scripts compare CLI output against these values.

Risks: changing constants can break broad expected-output coverage and should only follow intentional CID/profile changes. Test signal is exact expected hash matching across add, cat, object, dag, and gateway tests.
