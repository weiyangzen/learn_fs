## sources/control-plane/csi-driver-iscsi/.github/workflows/trivy.yaml

Purpose: builds the csi-driver-iscsi container and scans it for OS and library vulnerabilities with Trivy.

Control flow runs on master pushes and daily schedule, sets up Go 1.25.11, checks out code, builds a local `test/iscsi-csi:latest` image through `make test-container`, then scans it with pinned `aquasecurity/trivy-action`, all severities, and `ignore-unfixed`.

State is a local Docker image and Trivy database/cache. Dependencies include Docker buildx, Makefile, Dockerfile, Go, Trivy, and public ECR Trivy DB. Risks include Go version divergence from normal build workflows, full failure on all severities causing noise, and scan results depending on live vulnerability DB. Test signal is workflow failure on vulnerabilities or build errors.
