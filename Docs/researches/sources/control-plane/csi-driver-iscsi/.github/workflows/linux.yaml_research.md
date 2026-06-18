## sources/control-plane/csi-driver-iscsi/.github/workflows/linux.yaml

Purpose: primary Linux CI workflow for build, csi-sanity, and repository verification.

Control flow sets up Go `^1.18`, checks out code, runs `make`, then `make sanity-test` with `$HOME/.local/bin` added, followed by `./hack/verify-all.sh`. State includes built binaries, any sanity-test cluster/process artifacts, and generated verification diffs if checks mutate files.

Dependencies are Ubuntu, Go, Makefile, `test/sanity/run-test.sh`, and hack verify scripts. Risks include old Go relative to current dependencies, sanity-test environmental assumptions, and verify scripts that may install tools with apt/go. Test signal is workflow pass/fail.
