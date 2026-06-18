# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmushist.sh

Purpose: Reruns previously executed C-language litmus tests matching current criteria into a temporary results directory, then compares new outputs with historical outputs.

Important APIs/types/functions: Sources `scripts/parseargs.sh`; uses temp `$T`, `scripts/runlitmushist.sh`, and `scripts/cmplitmushist.sh`. Relies on `LKMM_DESTDIR` and `LKMM_PROCS`.

Control flow: Requires local `litmus` repo, creates temp mirrored results tree, builds a list of historical `.litmus.out` files under destination and filters out tests with too many processes, temporarily redirects `LKMM_DESTDIR` to temp results for rerun, copies new outputs back beside old outputs as `.new`, and invokes comparison script with destination-prefixed paths.

State and persistence: Creates temp results and writes `.new` output files next to historical outputs in `LKMM_DESTDIR`. Cleans temp directory on exit.

Dependencies/integration: Requires initialized litmus history via `initlitmushist.sh`, LKMM run/compare scripts, standard shell utilities, and accessible destination history.

Risks: Generated `cp` commands via `sed | sh` assume trusted path names. Existing `.new` files may be overwritten. If rerun fails, comparison may still proceed depending on downstream behavior. Path resolution via awk handles absolute vs relative destdir but remains shell-string based.

Test signals: Run after initialized history, missing litmus repo, custom destdir, process filters, intentional changed outputs, missing historical outputs, and existing `.new` files.
