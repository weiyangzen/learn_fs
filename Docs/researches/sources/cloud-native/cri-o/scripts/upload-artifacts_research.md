# sources/cloud-native/cri-o/scripts/upload-artifacts

This Bash script uploads a branch or tag marker file to the `gs://cri-o` Google Cloud bucket when `GCS_CRIO_SA` is provided. If the environment variable is empty, it prints a skip message and exits successfully.

Execution is linear with `set -euo pipefail`. When enabled, it writes the service account JSON to `/tmp/key.json`, authenticates with `gcloud`, determines the marker from `git rev-parse --abbrev-ref HEAD`, uses the current commit as the version, and if in detached HEAD assumes an exact tag, replaces the marker with the tag's major.minor substring and the version with the tag. It writes `latest-$MARKER.txt` and copies it to the bucket with `gsutil`.

State/persistence includes `/tmp/key.json`, a local marker file, and GCS object updates. Dependencies are git, gcloud, gsutil, and credentials. Risks include leaving credentials on disk, fragile `cut -c 2-5` major.minor extraction for multi-digit versions, assuming detached HEAD means exact tag, and no cleanup of marker files. No tests are present.
