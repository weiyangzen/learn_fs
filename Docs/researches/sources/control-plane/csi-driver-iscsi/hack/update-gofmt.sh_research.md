## sources/control-plane/csi-driver-iscsi/hack/update-gofmt.sh

Purpose: applies gofmt simplification to all non-vendor Go files.

Control flow runs `find . -name "*.go" | grep -v "/vendor/" | xargs gofmt -s -w` under strict bash. State is modified Go source files.

Dependencies are find, grep, xargs, and gofmt. Risks include filename splitting on whitespace, formatting generated files outside vendor, and requiring caller to run from repo root for intended scope. Test signal is `hack/verify-gofmt.sh`.
