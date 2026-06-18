## sources/control-plane/csi-driver-iscsi/hack/boilerplate/boilerplate.py

Purpose: repository-local boilerplate header checker for csi-driver-iscsi, adapted from Kubernetes scripts.

Important functions mirror the release-tools version: load header refs, enumerate files, strip Go build constraints and script shebangs, normalize years, diff against expected headers, and print failing paths. The root defaults three directories above the script, while the default boilerplate directory is built as `rootdir/csi-driver-nfs/hack/boilerplate`.

State is process-local file contents and regexes. Dependencies are Python standard libraries plus imported but unused `json` and `mmap`. Risks include the suspicious default boilerplate path referencing csi-driver-nfs, substring skip matching, unsupported extension key errors, and lack of focused tests. Test signal comes from `hack/verify-boilerplate.sh`.
