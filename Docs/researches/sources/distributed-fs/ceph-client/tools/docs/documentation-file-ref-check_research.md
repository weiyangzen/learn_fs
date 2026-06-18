# sources/distributed-fs/ceph-client/tools/docs/documentation-file-ref-check

Purpose: Perl tool that scans the kernel tree for references to `Documentation/...` files and reports or attempts to fix references to missing files.

Important APIs, types, and functions: Uses `Getopt::Long` for `--fix`, `--warn`, and help. `%false_positives` records accepted missing references. Step 1 scans Sphinx `:doc:` references and plain `Documentation/` references with `git grep`. Step 2, enabled by `--fix`, searches likely replacements and applies `sed` replacements.

Control flow: Exits early if not in a git tree. For `:doc:` references, resolves absolute or relative `.rst` targets and reports missing ones. For general references, filters Makefiles/scripts/hidden/build output/URLs/known patterns, normalizes punctuation and wrappers, checks glob existence, applies tools-relative exceptions, then reports or accumulates for fixing. Fix mode tries devicetree `.yaml`, basename searches, `.txt` to `.rst`, dash/underscore variants, and single-match replacement.

State and persistence: Normal mode is read-only. `--fix` edits files in place through `sed -i`.

Dependencies and integration points: Depends on git grep, find, sed, Perl, and kernel Documentation layout. Used by documentation maintenance.

Risks: Parsing is regex-based and intentionally heuristic. `--fix` can modify broad matches from `git grep -l` and requires manual review. Some generated or historical references need explicit false positives.

Test signals: Run normal/warn/fix modes on a controlled branch with missing docs, `:doc:` broken references, devicetree txt-to-yaml renames, multiple replacement candidates, and false positive entries.
