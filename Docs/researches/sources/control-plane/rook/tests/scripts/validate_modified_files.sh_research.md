<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_modified_files.sh -->
# sources/control-plane/rook/tests/scripts/validate_modified_files.sh

Purpose: CI guard ensuring generated files or build steps did not leave uncommitted changes after running make targets.

Important APIs and control flow: defines error messages by validation category. `validate` captures `git status --porcelain`, iterates non-empty output tokens, prints the category-specific error, full status, and `git diff`, then exits 1. The main case maps arguments such as `docs`, `helm-docs`, `codegen`, `modcheck`, `crd`, `build`, and `gen-rbac` to messages.

State, persistence, and integration: reads git worktree state and emits diffs; it writes nothing. Dependencies include git and a clean expected worktree after generation. Risks include iterating whitespace-split status output, noisy diffs for unrelated changes, and a typo in the build error string. Test signals are zero `git status --porcelain` output after the relevant CI step.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_modified_files.sh -->
