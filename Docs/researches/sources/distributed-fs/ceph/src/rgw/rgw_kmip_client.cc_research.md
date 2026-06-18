# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This file implements public KMIP request lifecycle: global manager binding, transceiver `send()`, blocking `wait()`, combined `process()`, and destructor cleanup for unique-id strings, locate lists, and key material. State is per-request in memory plus a global manager pointer; key output is zeroized on destruction. It integrates with concrete KMIP managers and RGW crypt/KMS callers. Risks include no coroutine suspension despite `optional_yield`, global manager ownership/deletion, raw pointer input ownership, and manager-specific shutdown errors. Tests should cover send/process/wait, output cleanup, key zeroization, and init/cleanup ownership.
