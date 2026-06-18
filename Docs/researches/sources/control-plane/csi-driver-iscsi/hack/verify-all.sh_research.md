## sources/control-plane/csi-driver-iscsi/hack/verify-all.sh

Purpose: aggregate verification entrypoint for csi-driver-iscsi.

Control flow resolves repo root and sequentially runs gofmt, govet, yamllint, boilerplate, spelling, and gomod verifiers. Golint is present but commented out. Strict bash stops on the first failure.

State may be modified by sub-checks such as `verify-gomod.sh`, which runs tidy/vendor before diffing. Dependencies are all hack verifier scripts and their tools. Risks include early exit hiding later failures, disabled golint, and checks that install tools with apt/go. Test signal is Linux workflow's verification step.
