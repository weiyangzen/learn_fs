# sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmus.sh

Purpose: Runs herd7 for a single litmus test, optionally translating C litmus to hardware assembly before hardware-model verification.

Important APIs and functions: Command API is `runlitmus.sh file.litmus`. It expects `LKMM_DESTDIR`, `LKMM_HERD_OPTIONS`, `LKMM_TIMEOUT_CMD`, and optional `LKMM_HW_MAP_FILE`/`LKMM_HW_CAT_FILE`. It calls `herd7`, `gen_theme7`, `jingle7`, and `scripts/simpletest.sh`.

Control flow: It validates the input file. For LKMM mode, or for hardware mode without a pre-existing LKMM output, it writes herd options into `litmus.out`, runs timed herd7, and exits in pure LKMM mode. Hardware mode then builds map/theme filenames, rejects complex synchronization tests, creates a theme, generates architecture litmus with jingle7, copies generation errors when no tests are produced, then runs herd7 on generated hardware litmus.

State and persistence behavior: Persists `.out`, hardware `.litmus.<HW>`, `.err`, and `.out` artifacts under `LKMM_DESTDIR`. Temporary theme and stderr files are removed by trap.

Dependencies and integration points: Called by `runlitmushist.sh`; hardware result filenames are coordinated with `hwfnseg.sh` and `judgelitmus.sh`.

Risks: Hardware path depends on external map/call/cat files. It skips complex synchronization for hardware rather than modeling it. Destination paths are only partly quoted. `jingle7` failure detection depends on a specific stderr phrase.

Test signals: Mock herd7/gen_theme7/jingle7 to cover LKMM success/failure, hardware simple/complex tests, generated-zero-tests, timeout propagation, and file naming.
