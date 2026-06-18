# sources/distributed-fs/coda/coda-src/lka/mklka.c

Purpose: command-line builder for lookaside databases. It walks a tree, computes SHA-1 for each plain file, and inserts `sha -> path` records into a new rwcdb database with a descriptor record.

APIs and flow: `main` parses `-v` and `-r`, canonicalizes database and tree paths, computes relative prefixes when requested, initializes rwcdb, writes the descriptor through `SetDescriptor`, and calls `WalkTree`. `WalkTree` uses `fts_open`, skips non-regular files, computes SHA via `ComputeViceSHA`, and inserts either absolute or relative paths.

State/persistence: writes a persistent rwcdb file and reports progress through stdout. Globals carry options and entry counts. Risks include fragile relative-prefix mutation, `open(nextf->fts_name)` instead of full `fts_path` in non-current directories, and no duplicate-hash policy beyond rwcdb behavior. Test signals are verbose output, `testlka`, and runtime `LookAsideAndFillContainer`.
