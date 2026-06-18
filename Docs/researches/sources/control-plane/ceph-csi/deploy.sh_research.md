# sources/control-plane/ceph-csi/deploy.sh

Purpose: release automation script that builds/pushes multi-architecture Ceph-CSI images and publishes RBD/CephFS Helm charts to `ceph/csi-charts`.

Important APIs/types/functions: `build_push_images` inspects base-image manifests, runs qemu-user-static, builds `amd64`/`arm64` images via make, creates manifests, and pushes. `push_helm_charts` rewrites chart metadata for release branches, rsyncs chart content, packages with Helm, indexes the repo, commits, and pushes.

Control flow: requires `GITHUB_TOKEN`; builds images first; creates temp chart checkout; installs Helm from configured script/version; clones chart repo; pushes RBD then CephFS charts; removes temp dir.

State and persistence behavior: mutates Docker registry state, local temp checkout, chart files in that checkout, git history in `ceph/csi-charts`, and remote chart index. Does not commit in this source repo.

Dependencies and integration points: Docker manifest/build, jq, qemu-user-static, make targets, Helm installer, curl, git, rsync, build env, and GitHub token.

Risks: `sed` rewrites are branch/version-sensitive. Docker experimental manifest behavior and multiarch base digests can fail. Token in push URL must be protected. Temp cleanup is simple and not trap-based.

Test signals: release CI logs, image manifest inspection, Helm package/index validation, and chart repository publication.
