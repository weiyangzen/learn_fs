## sources/control-plane/csi-driver-iscsi/hack/verify-gomod.sh

Purpose: verifies go.mod/go.sum/vendor are tidy and current.

Control flow enables module mode, runs `go mod tidy`, `go mod vendor`, then checks `git diff`; any diff is printed and treated as failure. State is intentionally mutated before diffing.

Dependencies are Go modules, vendor mode, git, and network/module cache. Risks include leaving working tree changes after failure, broad `git diff` detecting unrelated pre-existing modifications, backtick command substitution style, and no path-specific diff. Test signal is Linux verify-all workflow.
