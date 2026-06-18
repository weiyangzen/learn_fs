## sources/control-plane/longhorn-engine/scripts/version

### Purpose
`scripts/version` computes shell variables describing the current Longhorn engine source version for build and packaging scripts.

### Important APIs, Types, And Functions
It sets `DIRTY` when tracked files have uncommitted changes, `COMMIT` from `git rev-parse --short HEAD`, `GIT_TAG` from the first tag containing HEAD, `VERSION` from a clean containing tag or from commit plus dirty suffix, `GITCOMMIT` from the full hash, and `BUILDDATE` from UTC RFC3339 seconds with `T` separator.

### Control Flow
The script is intended to be sourced. It branches on clean tagged state versus commit-derived state.

### State, Persistence, And Dependencies
It writes no files, only shell variables. It depends on git and GNU `date --rfc-3339=seconds`.

### Integration Points
`scripts/package` sources it to determine image tags and build metadata.

### Risks
`git tag -l --contains HEAD | head -n 1` can choose an arbitrary tag when multiple tags contain a commit. Untracked files are ignored for dirty detection.

### Test Signals
Checks should verify clean tagged, clean untagged, and dirty tree outputs.
