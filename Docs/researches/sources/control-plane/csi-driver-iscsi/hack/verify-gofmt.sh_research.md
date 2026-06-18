## sources/control-plane/csi-driver-iscsi/hack/verify-gofmt.sh

Purpose: checks that all non-vendor Go files are gofmt-simplified.

Control flow captures `gofmt -s -d` output over files found by `find|grep|xargs`, prints the diff and guidance when non-empty, and exits nonzero. State is read-only.

Dependencies are gofmt and shell utilities. Risks include filename splitting, checking generated files outside vendor, and command substitution storing large diffs in memory. Test signal is `verify-all.sh` and Linux workflow.
