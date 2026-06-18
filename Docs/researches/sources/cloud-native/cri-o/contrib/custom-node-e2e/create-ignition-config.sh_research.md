# sources/cloud-native/cri-o/contrib/custom-node-e2e/create-ignition-config.sh

Purpose: build CRI-O from source, upload bundle artifacts, and generate a Fedora CoreOS ignition file for Kubernetes node e2e testing with custom CRI-O.

Important APIs and control flow: parses required `-d CRIO_DIR`, `-i IGNITION_OUT_DIR`, `-b GCS_BUCKET_NAME`, optional service account and extra config paths. It cleans the repo, builds `pinns`, runs static build, detects local architecture as amd64 or arm64, copies static binaries into an arch-specific directory, builds docs and config, runs `make bundle`, uploads artifacts through `upload-artifacts.sh`, verifies bundle SHA against the latest branch marker, embeds extra config files into numbered `/etc/crio/crio.conf.d/*.conf` snippets, creates a randomized node-e2e installer script that downloads CRI-O from GCS, adjusts SELinux labels, removes podman CNI config, sets debug logging, writes runtime/infra config snippets, starts `crio.service`, uploads that installer to GCS, and writes an ignition JSON that disables Zincati updates and installs dbus-tools plus the CRI-O installer service.

State and persistence: modifies build outputs, `bin/static-$ARCH`, bundle artifacts, latest marker files, GCS bucket contents, temp installer script, and the output `.ign` file.

Dependencies and integration: requires sudo, make, Nix static build, GCS/gsutil, gcloud optional auth, git, md5sum, curl, systemd, rpm-ostree, SELinux tools, and CRI-O bundle scripts.

Risks: the script writes shell and JSON through heredocs with embedded config content; unusual config contents could break generated scripts. It assumes branch marker naming, architecture mapping, and Fedora CoreOS paths.

Test signals: successful bundle upload, SHA marker match, installer upload, and generated ignition file; real validation comes from node e2e boot/install runs.
