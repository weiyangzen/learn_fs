## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum.go

**Purpose:** Implements deterministic tar stream checksumming and optional recompressed/identity tar streaming for builder cache keys and archive context hashes.

**Important APIs/types:** `NewTarSum`, `NewTarSumHash`, `NewTarSumForLabel`, `TarSum`, `tarSum`, `THash`, `NewTHash`, `DefaultTHash`, `encodeHeader`, `initTarSum`, `Read`, `Sum`, and `GetSums`.

**Control flow:** `Read` lazily streams tar data: it reads current file data, hashes selected header fields and content, writes through a tar writer, flushes through gzip or nop writer, advances headers on EOF, records per-file sums, and marks finished at archive EOF. `Sum` sorts file sums by checksum and hashes all sums plus optional extra bytes with a version/hash label prefix.

**State and persistence:** Maintains reader/writer buffers, current hash, file counter, current file name, per-file sums, compression setting, version, and hash provider. No durable state.

**Dependencies and integration:** Used by `remotecontext.FromArchive` and file hash compatibility. Depends on archive/tar, gzip, crypto hash providers, and version-specific header selectors.

**Risks:** Streaming state machine is subtle; EOF handling, writer flushing, compression mode, duplicate paths, and header selection all affect cache compatibility. Only SHA-256/SHA-512 labels are accepted for standard hashes.

**Test signals:** Tarsum tests outside the listed subset cover labels, empty tars, read sizes, iteration, checksums, and benchmarks. Listed `fileinfosums` and builder-context tests cover supporting behavior.
