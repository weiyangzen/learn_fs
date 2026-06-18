# sources/distributed-fs/openafs/src/NTObjdir

Purpose: shell helper for creating the OpenAFS Windows NT object directory tree from a Unix host before the native Windows build tooling was fully ported.

Important APIs/types/functions: it defines a large `dirs` whitespace list covering `config`, many `WINNT/...` components, language-resource folders, and core AFS server/library/test directories. It checks for `src`, `i386_nt40`, and executable `src/WINNT/docs/build/ntobjdirs`, then invokes `ntobjdirs -d <dir>` for each listed path.

Control flow: the script must be run from the directory above `src`. It fails early with explanatory messages if the required source tree, NT object root, or helper script is absent. For each directory entry it echoes and runs the helper command.

State/persistence: no internal state beyond the `dirs` variable. Persistence is external: the helper creates directories under the NT object directory layout.

Dependencies/integration: depends on `/usr/bin/sh`, the OpenAFS source tree layout, the `i386_nt40` object directory, and `src/WINNT/docs/build/ntobjdirs`. It integrates with legacy Windows build preparation rather than runtime OpenAFS behavior.

Risks/test signals: the hard-coded directory list can drift from the real source tree, and whitespace/line-continuation errors would silently skip or split paths. Tests are practical smoke checks: run from a fixture tree and assert every intended directory is passed once to `ntobjdirs`.
