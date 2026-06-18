# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkalllitmus.sh

Purpose: Runs LKMM checking over all top-level `.litmus` files in `litmus-tests` and reports whether results match embedded expected `Result:` comments.

Important APIs/types/functions: Shell script sourcing `scripts/parseargs.sh`; uses `LKMM_DESTDIR`, `LKMM_HW_MAP_FILE`, `scripts/simpletest.sh`, and `scripts/checklitmus.sh`.

Control flow: Validates `litmus-tests` is accessible, mirrors directories into destination when needed, iterates `litmus-tests/*.litmus`, skips non-simple tests for hardware translation mode, runs each through `checklitmus.sh`, accumulates failure status, and prints success or verification mismatch summary to stderr.

State and persistence: Writes `.out` files through downstream scripts into `LKMM_DESTDIR`. Creates destination directories when not using `.`.

Dependencies/integration: Requires LKMM environment from `parseargs.sh`, litmus-tests directory, herd/runlitmus/judgelitmus tooling, and optional hardware mapping support.

Risks: Only checks top-level `litmus-tests/*.litmus`, not recursive subdirectories. Unquoted `$litmusdir`/`$i` are acceptable for expected paths but fragile with spaces. Directory mirroring via generated shell commands assumes trusted path names.

Test signals: Run with default, custom `--destdir`, `--hw`, missing/inaccessible litmus-tests, passing fixtures, and intentionally mismatched `Result:` comments.
