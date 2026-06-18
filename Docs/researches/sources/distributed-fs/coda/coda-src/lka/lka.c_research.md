# sources/distributed-fs/coda/coda-src/lka/lka.c

Purpose: runtime manager for Coda lookaside databases. Venus can register one or more rwcdb databases mapping SHA-1 object hashes to local file paths, then use those paths to fill container files without fetching data remotely.

APIs and flow: `LKParseAndExecute` parses `cfs lka` commands (`--list`, `--clear`, `+db`, `-db`) and manages a global linked list of `lkdb` objects. `lkdb_BindDB` opens an absolute database path, validates the descriptor record, derives the database directory, and counts entries. `LookAsideAndFillContainer` scans databases for a SHA, avoids paths under the Coda prefix, copies the hit file to the container while recomputing SHA, and validates optional length.

State/persistence: global `lkdbchain` holds open rwcdb handles and per-db statistics. The database itself persists as rwcdb content with descriptor key zero. Risks include no duplicate registration checks, command parsing with fixed buffers, use of `open` result without checking before copy, and path prefix handling for relative records. Test signals include `testlka` and `mklka` round trips.
