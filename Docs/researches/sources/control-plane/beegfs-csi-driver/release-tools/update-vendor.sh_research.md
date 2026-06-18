# sources/control-plane/beegfs-csi-driver/release-tools/update-vendor.sh

Purpose: Updates vendored dependencies for repositories using either dep or Go modules.

Important APIs/types/functions: Checks for `Gopkg.toml` to run `dep ensure`; checks for `go.mod` to run `release-tools/verify-go-version.sh "go"` followed by `GO111MODULE=on go mod tidy` and `go mod vendor`.

Control flow: Branches by dependency management file presence. For Go modules it warns on unexpected Go version before tidying and vendoring.

State and persistence: Mutates `vendor/`, `go.mod`, and `go.sum` for module repos, or dep-managed vendor state for dep repos.

Dependencies and integration points: Used manually or by release/update workflows. Requires `dep` for old repos or Go tooling for modules, plus local `release-tools/verify-go-version.sh`.

Risks: Does nothing silently if neither `Gopkg.toml` nor `go.mod` exists. Go version mismatches only warn, so output may differ across Go versions. Vendor updates can be large and require review.

Test signals: No built-in test run; callers should run project tests and inspect dependency diffs.
