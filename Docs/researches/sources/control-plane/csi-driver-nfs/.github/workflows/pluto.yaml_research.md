# sources/control-plane/csi-driver-nfs/.github/workflows/pluto.yaml

Purpose: checks Kubernetes manifest API versions for deprecations with Fairwinds Pluto.

Important APIs and types: triggers on pushes and PRs. Downloads Pluto through a pinned action, then runs `pluto detect-files -d deploy` and `pluto detect-files -d deploy/example`.

Control flow: checkout, install Pluto, scan deployment directories.

State and persistence: no repo writes; workflow output only.

Dependencies and integration: validates Kubernetes YAML outside the Helm chart templates assigned here.

Risks: only scans `deploy` and `deploy/example`, not `charts`. Pluto version comes from pinned action but its API deprecation database may need updates.

Test signals: Pluto workflow pass/fail.
