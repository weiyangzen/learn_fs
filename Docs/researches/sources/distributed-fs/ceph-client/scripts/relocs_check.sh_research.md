# sources/distributed-fs/ceph-client/scripts/relocs_check.sh

Purpose: `relocs_check.sh` produces a filtered list of suspicious dynamic relocations in `vmlinux` for architecture-specific relocation checkers. It removes relocations known to be legitimate due to unresolved weak symbols.

Important APIs, types, and functions: it accepts three positional arguments: objdump path, nm path, and vmlinux path. It builds `undef_weak_symbols` with `nm "$vmlinux" | awk '$1 ~ /w/ { print $2 }'`, then pipes `$objdump -R "$vmlinux"` through a relocation grep and an optional fixed-string word exclusion for weak symbols.

Control flow: the script has no option parsing. It computes weak undefined names first, then streams objdump relocation rows containing `R_`. If the weak-symbol set is non-empty, `grep -F -w -v` drops matching rows; otherwise the stream is passed through unchanged.

State and persistence: it is stateless and writes only to stdout/stderr through its child commands.

Dependencies and integration points: used by architecture relocation validation scripts after vmlinux link. It depends on GNU-style `objdump -R` and `nm` output and on `awk`, `grep`, and shell pipelines.

Risks: the weak-symbol awk pattern is broad and tied to nm column formatting. Filtering by symbol name can hide rows if names collide unexpectedly. The script does not `set -e`, so failures may be represented only through pipeline exit behavior in callers.

Test signals: feed a vmlinux with known weak unresolved symbols and known bad relocations, verify weak relocations are removed and bad relocations remain. Tool absence and empty weak-symbol cases should be exercised.
