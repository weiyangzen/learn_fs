<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/generate-authors.sh -->
# sources/cloud-native/containers-storage/hack/generate-authors.sh

## Purpose
This helper regenerates the repository `AUTHORS` file from git history.

## Important APIs, Types, And Functions
It changes to the repository root, writes a fixed header, then appends unique author names/emails from `git log --format='%aN <%aE>'` sorted with `LC_ALL=C.UTF-8 sort -uf`.

## Control Flow
`set -e` aborts on failure. Output is redirected atomically only at shell-redirection granularity to `AUTHORS`.

## State And Persistence
It overwrites `AUTHORS` in the repository root.

## Dependencies And Integration Points
It depends on git history and `.mailmap` behavior for deduplication.

## Risks And Test Signals
Running outside a git checkout or without expected locale support can fail. The write is not temp-file atomic, so interruption could leave a partial `AUTHORS`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/generate-authors.sh -->
