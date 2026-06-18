# sources/control-plane/csi-driver-nfs/.github/workflows/trivy.yaml

Purpose: builds the NFS plugin image and scans it for OS and library vulnerabilities with Trivy.

Important APIs and types: runs on pushes to master and pull requests. Installs Go `1.25.11`, sets build env (`PUBLISH`, `REGISTRY`, `IMAGE_VERSION`, `ARCH`), runs `make nfs` and `make container-build`, then scans `test/nfsplugin:latest-linux-amd64` with pinned Trivy action and ECR-hosted DB.

Control flow: checkout, setup Go, build binary/image, scan image, fail on any severity because `exit-code: 1`.

State and persistence: creates local Docker image and vulnerability scan logs.

Dependencies and integration: depends on Docker buildx, Makefile targets, Dockerfile, Go, and Trivy DB.

Risks: Go version is very specific and may not exist in setup-go at all times. Scanning all severities including unknown can cause noisy failures. `ignore-unfixed` may still pass known unfixed vulnerabilities.

Test signals: successful image build and Trivy pass/fail.
