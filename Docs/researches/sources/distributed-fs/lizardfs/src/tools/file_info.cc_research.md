# sources/distributed-fs/lizardfs/src/tools/file_info.cc

Purpose: Implements `lizardfs fileinfo`, which reports tape replicas and per-chunk storage locations/parts for a file.

Important APIs/types/functions: `file_info_run`; static `file_info`; static `chunks_info`; `chunkTypeToString`; `cltoma::tapeInfo`; `matocl::tapeInfo`; `cltoma::chunksInfo`; `matocl::chunksInfo`; `ChunkCopiesCalculator`.

Control flow: For each file, the command opens a master connection, requests tape info and decodes status-or-response packet versions, then pages through chunk info in batches of 100 until fewer than 100 entries are returned. For each chunk it prints id/version, sorted chunk part addresses/labels, and redundancy warnings.

State and persistence: Read-only; uses master metadata, chunk location state, and tape-copy state. Formatting state is local.

Dependencies and integration: Uses the newer typed protocol helpers and `ServerConnection`-style framing manually through `tcpwrite`/`tcptoread`. It integrates with tape server and chunkserver reporting through `matocl` payloads.

Risks and test signals: Timeout behavior is controlled by `-l` (10 seconds vs simulated 10 days). Manual packet-version handling must match `matocl.h`. The code warns about no valid copies/not enough parts but does not repair. No direct tests in this subset.
