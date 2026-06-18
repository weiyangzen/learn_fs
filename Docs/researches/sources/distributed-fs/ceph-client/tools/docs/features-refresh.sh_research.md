# sources/distributed-fs/ceph-client/tools/docs/features-refresh.sh

Purpose: Regenerates architecture support tables under `Documentation/features/*/*/arch-support.txt` by scanning arch Kconfig files for configured feature symbols.

Important APIs, types, and functions: Shell loop over feature files; extracts `#         Kconfig:` line; supports plain `K` and negated `!K`; scans `arch/*/Kconfig*`; writes a temporary table and moves it into place.

Control flow: For each feature file, determine operator and Kconfig token, warn if the token is invalid across all arches, write preserved comment header and table header, iterate architectures, set status to `ok` when the feature rule matches, otherwise preserve existing status row or default to `TODO`, close table, and replace original file.

State and persistence: Mutates every `arch-support.txt` file in place through temporary files.

Dependencies and integration points: Depends on being run from kernel tree root with Documentation/features and arch directories. Uses grep, find, sed, shell globbing.

Risks: `grep "$K"` is substring-based rather than Kconfig-symbol aware. Invalid negated features can still be rewritten. No `set -e`, so command failures may continue. Existing non-comment rows are preserved only by matching `" $ARCH:"`.

Test signals: Run on a clean tree and inspect diff, features with normal and negated Kconfig symbols, renamed/missing Kconfig tokens, and arch additions/removals.
