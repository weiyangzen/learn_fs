# sources/cloud-native/ostree/hack/provision-packit.sh

Purpose: transforms a Packit package-mode test VM into an ostree image-mode system by building a bootc container containing Packit-built ostree RPMs and installing it alongside the current filesystem.

Important APIs/functions: temp workspace `OSTREE_TEMPDIR`, copies of hack files, `/var/ARTIFACTS`, `/var/share/test-artifacts`, tmt scripts or `/usr/local/bin`, `/etc/os-release`, base image selection by `ID-VERSION_ID`, optional RHEL nightly compose repo generation, `podman build --from`, and privileged `podman run ... bootc install to-filesystem --replace=alongside`.

Control flow: create temp dir with cleanup trap, copy artifacts and helper scripts, determine architecture and OS, select CentOS/Fedora bootc base or reject unsupported OS, optionally configure RHEL nightly compose repos, copy Packit COPR repo and integration tests, build `localhost/ostree:latest` using `Containerfile.packit`, then run bootc install into `/target`.

State and persistence: writes temporary build context, may add RHEL repo to `/etc/yum.repos.d`, builds a local container image, mounts and mutates the host root filesystem for next boot. The temp workspace is removed on exit.

Dependencies and integration: integrates Packit/TMT artifacts, podman, bootc, skopeo, jq, curl, nightly compose infrastructure, test-artifacts repo, and `Containerfile.packit`.

Risks and test signals: high-risk privileged host mutation, network dependence, unsupported distro branching, RHEL path assumptions, and container build context leakage. Signals are successful podman build, bootc install completion, reboot into image mode, and Packit/TMT follow-up tests.
