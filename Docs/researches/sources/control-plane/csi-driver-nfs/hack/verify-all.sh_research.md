<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-all.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-all.sh

## Purpose
Runs the main repository verification suite from the git root.

## Important APIs, Types, and Functions
The script computes `PKG_ROOT="$(git rev-parse --show-toplevel)"` and sequentially invokes `verify-gofmt.sh`, `verify-govet.sh`, `verify-yamllint.sh`, `verify-boilerplate.sh`, `verify-helm-chart-files.sh`, `verify-helm-chart.sh`, `verify-helm-chart-index.sh`, and `verify-gomod.sh`.

## Control Flow, State, and Persistence
With `set -euo pipefail`, the first failing verification stops the suite. It mainly checks repository state but some child scripts can install tools or regenerate module/vendor files before diffing.

## Dependencies and Integration Points
It integrates all local CI gates for formatting, vet, YAML, license headers, Helm packaging/index, chart image parity, and Go modules. It depends on the transitive tools required by each child script.

## Risks and Test Signals
Risks include non-hermetic behavior because child scripts may install packages from the network, mutate files before checking diffs, or require cluster-independent tool availability. Signals are all child scripts exiting zero and no unexpected git diff after verification.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-all.sh -->
