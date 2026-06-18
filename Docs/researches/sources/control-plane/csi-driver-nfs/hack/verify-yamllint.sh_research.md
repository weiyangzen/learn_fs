<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-yamllint.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-yamllint.sh

## Purpose
Validates YAML formatting for deployment, example, and Helm chart manifests, while enforcing parity between raw deploy YAML count and Helm template count.

## Important APIs, Types, and Functions
The script installs `yamllint` through apt if missing, sets `LOG=/tmp/yamllint.log`, counts `deploy/*.yaml` and chart template YAMLs excluding serviceaccount, then runs `yamllint -f parsable` over several deploy/example globs and the latest chart templates. It filters accepted warnings such as line length and chart-template syntax noise.

## Control Flow, State, and Persistence
It first compares YAML file counts between deploy manifests and Helm templates. Then it lints each path group, filters known noisy messages and CRD snapshot long lines, and exits if any remaining issue appears. It may install packages and writes a temporary log.

## Dependencies and Integration Points
It depends on apt, yamllint, shell globs, chart layout, deploy layout, and generated CRD exceptions. It is part of `verify-all.sh`.

## Risks and Test Signals
Risks include package-manager side effects, brittle file-count parity, unquoted globs, CRD exceptions hiding real issues, and Helm templates not being valid plain YAML. Signals are matching file counts and zero unfiltered yamllint messages.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-yamllint.sh -->
