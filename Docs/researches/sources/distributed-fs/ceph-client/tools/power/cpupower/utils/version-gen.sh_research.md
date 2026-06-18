# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/version-gen.sh

## Purpose
Generates the version string used when building cpupower utilities.

## Important APIs, Types, and Functions
It checks for a kernel git repository three directories up, tries `git describe --abbrev=4 HEAD`, refreshes the index, appends `-dirty` when the worktree differs from HEAD, normalizes hyphens to dots, otherwise reads `VERSION`, `PATCHLEVEL`, `SUBLEVEL`, and `EXTRAVERSION` from the kernel Makefile. It strips an optional leading `v` and echoes the result.

## Control Flow, State, and Persistence
The script is side-effect light except `git update-index -q --refresh`, which refreshes git index stat information. It does not write output files directly; build rules capture stdout.

## Dependencies and Integration Points
Depends on POSIX shell, git when in a git checkout, grep/tr, expr, and being run from `tools/power/cpupower/` so relative paths resolve to the kernel root.

## Risks and Test Signals
Fallback `eval` of Makefile variables assumes trusted local Makefile content. Running from another directory returns wrong paths. Test in git and exported tarball trees, dirty worktree, annotated/non-v tags, and Makefile-only version fallback.
