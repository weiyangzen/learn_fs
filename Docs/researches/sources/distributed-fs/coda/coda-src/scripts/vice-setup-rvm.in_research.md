# sources/distributed-fs/coda/coda-src/scripts/vice-setup-rvm.in

Purpose: interactive setup for Coda server RVM log/data areas and server configuration.

Control flow: loads `server.conf` if present, rejects existing `-rvm` line in old `srv.conf`, explains RVM tradeoffs, prompts for log file/partition and size, data file/partition and size, normalizes paths, converts data size to MB/bytes, warns before wiping, initializes the log with `rvmutl`, computes static/reserved/heap sizes and RVM start/list/chunk parameters, writes `rvm_log`, `rvm_data`, and `rvm_data_length` through `codaconfedit` or appends old-style `-rvm`, then runs `rdsinit`.

State/persistence: may wipe/init RVM log and data files or raw partitions, and writes server config. It directly creates persistent metadata storage.

Dependencies, risks, tests: requires `rvmutl`, `rdsinit`, `codaconfedit`, operator privilege, and accurate device choices. Risks include raw device destruction, unchecked arithmetic for too-small data sizes, assumptions about <=4 meaning GB, no noninteractive mode, and `set -e` terminating on unexpected command failures. Test with file-backed RVM in a temp area, unsupported sizes, existing srv.conf guard, config write path, and failed `rvmutl`/`rdsinit`.
