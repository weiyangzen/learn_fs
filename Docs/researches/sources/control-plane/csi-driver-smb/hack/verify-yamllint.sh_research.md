# sources/control-plane/csi-driver-smb/hack/verify-yamllint.sh

## Purpose
Runs yamllint over deploy and example YAML files while ignoring line-length findings.

## Important APIs, Types, and Functions
Installs yamllint with apt if absent, writes lint output to `/tmp/yamllint.log`, filters "line too long", counts remaining findings, and fails if any remain.

## Control Flow
Loops over fixed glob patterns under `deploy/` and `deploy/example/`, runs yamllint, prints findings, and exits on first non-line-length issue.

## State and Persistence
May install yamllint. Writes `/tmp/yamllint.log`.

## Dependencies
Requires apt, yamllint, shell glob matching, and deploy/example layout.

## Integration Points
Called by `verify-all.sh`.

## Risks and Edge Cases
Unmatched globs may be passed literally. Shared `/tmp/yamllint.log` can be clobbered. Auto-installing packages requires root and network.

## Test Signals
All checked patterns print no remaining lint findings and final success message.
