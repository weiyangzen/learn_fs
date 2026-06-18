# sources/distributed-fs/ceph-client/scripts/tools-support-relr.sh

Purpose: `tools-support-relr.sh` probes whether the configured compiler/binutils pipeline supports RELR packed relative relocations well enough for kernel use.

Important APIs, types, and functions: it creates a temporary C object defining `void *p = &p;`, links it as a shared object with either LLD `--pack-dyn-relocs=relr` or GNU/compatible `-z pack-relative-relocs`, verifies `nm` can inspect it without stderr output, and runs `objcopy -O binary`.

Control flow: `set -eu` aborts on unset variables or failures. A trap removes temp files. If the LLD-style option fails, it tries the `-z` form and treats an error mentioning `pack-relative-relocs` as unsupported.

State and persistence: only temporary files under `mktemp`, removed on exit.

Dependencies and integration points: used by Makefiles/Kconfig probes for RELR support. Depends on `CC`, `LD`, `NM`, and `OBJCOPY` environment variables.

Risks: tool diagnostics are parsed by substring, so message changes can affect detection. GNU nm's zero exit with RELR stderr is explicitly handled by requiring empty stderr.

Test signals: run with supported binutils, old LLD before 15, unsupported GNU ld, and nm versions that print RELR errors.
