# sources/distributed-fs/ceph-client/tools/net/ynl/ynl-regen.sh

Purpose: regeneration helper for files containing YNL generation markers. It finds generated C/header/UAPI outputs and reruns `pyynl/ynl_gen_c.py` with the recorded mode, header/source kind, spec, and optional arguments.

Important flow: parses `-f` to force and `-p <path>` to search outside the kernel root. Computes `TOOL` relative to itself and `KDIR` as the kernel root. Inside the search directory, `git grep` finds files matching `/* YNL-GEN kernel|uapi|user */`; a second grep/sed extracts the spec path and generation parameters, and `YNL-ARG` lines supply extra args. Files newer than their YAML spec are skipped unless forced. Generation uses `--cmp-out` to avoid rewriting identical output.

State/dependencies: depends on git, sed, bash arrays, generated marker comments, and source tree layout. It writes generated files in place.

Risks/test signals: marker parsing assumes the expected comment shape and parameter positions. Search under a non-git or shallow tree fails. Good signals are idempotent reruns with no changed files and successful forced regeneration after spec edits.
