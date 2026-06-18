# sources/control-plane/mayastor/scripts/check-submodule-branches.sh

Purpose: verifies submodule HEADs are contained in the branch configured in `.gitmodules`.

Important APIs/types/functions: `submodule_check` iterates `git config --file .gitmodules --get-regexp path`, reads `submodule.<path>.branch`, and checks `git branch -r --contains HEAD` for `origin/<branch>`.

Control flow: enters repo root, loops submodules with file-style `.git`, records any failure, and exits `1` if at least one submodule is off-branch.

State/persistence: read-only git state.

Dependencies/integration: CI/release guard for submodule branch hygiene.

Risks: skips submodules whose `.git` is a directory rather than file. Unquoted variables can break on paths with spaces, though submodule paths likely do not contain spaces.

Test signals: clean exit means every initialized submodule HEAD is reachable from its configured remote branch.
