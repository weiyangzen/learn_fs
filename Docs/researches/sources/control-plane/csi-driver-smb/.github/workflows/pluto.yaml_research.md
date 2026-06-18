## sources/control-plane/csi-driver-smb/.github/workflows/pluto.yaml

Purpose: detects deprecated or removed Kubernetes API versions in deployment manifests. It runs on push and pull request.

Important flow: checkout, install the pinned FairwindsOps Pluto action, run `pluto detect-files -d deploy --ignore-deprecations --ignore-removals`, then run `pluto detect-files -d deploy/example` without those ignores.

State is read-only manifest scanning. Dependencies are the Pluto action and the deploy/example trees. Risks include ignores making the main deploy folder less strict, scan scope excluding charts, and action version drift despite pinning. Test signal is CI failure when manifests use unsupported API versions according to Pluto.
