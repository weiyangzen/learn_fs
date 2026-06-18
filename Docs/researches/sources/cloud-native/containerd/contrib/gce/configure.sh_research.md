# sources/cloud-native/containerd/contrib/gce/configure.sh

Purpose: privileged GCE node installer that fetches containerd/Kubernetes metadata, downloads or uses a preloaded CRI containerd tarball, installs it under `/home/containerd`, and writes the CRI plugin configuration used by kubelet.

Important APIs/functions: `fetch_metadata` queries instance attributes with the required metadata header. `fetch_env` reads YAML metadata such as `kube-env` and `containerd-env`, converts it to readonly shell assignments using Python/YAML, and sources the result. `is_preloaded` checks Kubernetes preload metadata. The main script resolves test/production deployment paths, package prefix, version, tarball name, optional GCS bearer token, and architecture-specific download path.

Control flow and state: strict shell options are enabled. It detects Python 2/3, sources metadata env files, optionally obtains `GCS_BUCKET_TOKEN`, resolves `CONTAINERD_VERSION`, downloads or skips a preloaded tarball, extracts it, removes bundled `crictl`, writes `/etc/containerd/config.toml`, writes Docker Hub mirror host config, writes `/etc/profile.d/containerd_env.sh`, and optionally runs a metadata-supplied test init script. State persists in `/home/containerd`, `/etc/containerd`, and profile/systemd-visible paths.

Dependencies and integration: GCE metadata, curl, YAML Python module, jq for some test paths, sha1sum, tar, Kubernetes GCE env variables, containerd CRI config v2, CNI locations, mirror.gcr.io, and optional extra runtime metadata.

Risks: metadata parsing uses `eval` of generated shell declarations, so correctness of YAML quoting is critical. The tarball name defaults to `linux-amd64` even though `aarch64` uses a GitHub arm64 URL, making architecture handling subtle. Missing version/preload data aborts. Secret token handling disables xtrace briefly but curl command structure still deserves care.

Test signals: no direct tests. Useful checks are generated TOML validity, containerd startup with CRI required plugin, CNI template selection for netd/network policy, authenticated GCS downloads, and test-mode extra init execution.
