## sources/control-plane/csi-driver-smb/.github/workflows/trivy.yaml

Purpose: scans the SMB CSI container image for OS and library vulnerabilities on master pushes and pull requests.

Important flow: setup Go 1.25.11, checkout, build a local image by setting `PUBLISH=true`, `REGISTRY=test`, `IMAGE_VERSION=latest`, and running `make container`, then run pinned `aquasecurity/trivy-action` against `test/smb-csi:latest` with table output and exit code 1 for all severities.

State includes the local Docker image and Trivy DB cache. Dependencies are Docker, Makefile container target, Trivy action, and the public ECR Trivy DB repository. Risks include scanning only the Linux image, high noise from LOW/UNKNOWN severity failures, and network/DB availability. Test signal is vulnerability gate failure.
