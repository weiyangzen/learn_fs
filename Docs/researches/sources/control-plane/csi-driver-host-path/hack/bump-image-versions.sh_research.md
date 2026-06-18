# sources/control-plane/csi-driver-host-path/hack/bump-image-versions.sh

## Purpose
This maintenance script updates sidecar image tags in all deployment files to the latest release tags found in `registry.k8s.io/sig-storage`. It is intended as a helper for release maintenance, not an automatic commit generator.

## Important APIs, Types, And Functions
The script is POSIX `sh` with `set -e` and `set -x`. It defines an `images` list containing CSI sidecars and liveness probe images, checks for `skopeo` and `jq`, then loops over each image. For each image, it runs `skopeo list-tags --retry-times 3`, uses `jq` to list tags, filters tags beginning with `v`, sorts with `sort -V`, selects the last tag, and runs `find deploy -type f -exec sed -i '' ...` to rewrite matching image lines.

## Control Flow
Dependency checks happen first. The loop queries registry tags one image at a time. The substitution replaces any line starting with `image: registry.k8s.io/sig-storage/$image:` with the same prefix and the latest discovered tag. The introductory comment warns maintainers not to commit all changes blindly because older Kubernetes deployments may need older sidecars.

## State, Persistence, And Dependencies
The script edits files under `deploy/` in place. It depends on network access to the registry, `skopeo`, `jq`, `grep`, `sort -V`, `find`, and a BSD/macOS-style `sed -i ''` invocation.

## Integration Points
It updates the image tags that deploy scripts parse for image override defaults and RBAC version derivation. It affects Kubernetes deployment manifests across all versioned deployment directories.

## Risks
`sed -i ''` is not portable to GNU sed without different syntax, so Linux runs may fail. Latest sidecar tags may be incompatible with older deployment manifests or Kubernetes versions. The script does not update RBAC files directly; deploy scripts fetch RBAC based on tags at runtime.

## Test Signals
Run in a disposable branch, inspect `git diff`, verify only intended image lines changed, and deploy each supported manifest variant against its target Kubernetes version before committing any updates.
