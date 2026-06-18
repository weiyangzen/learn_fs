## sources/control-plane/csi-driver-iscsi/hack/release-image.sh

Purpose: Azure Container Registry release helper, apparently copied from an NFS CSI workflow.

Control flow requires a registry name, exports ACR-derived registry variables, sets `IMAGENAME=public/k8s/csi/nfs-csi`, logs into Azure ACR, runs `make container push push-latest`, sleeps, pulls `mcr.microsoft.com/k8s/csi/nfs-csi:latest`, and inspects creation time.

State includes Docker login, pushed images, and local pulled image. Dependencies are Azure CLI, Docker, Make targets, and registry naming. Risks are severe for this repo: image names reference NFS rather than iSCSI, Makefile targets `push`/`push-latest` may not exist locally, variables are unquoted, and it can publish to external registries. Test signal is manual command success only.
