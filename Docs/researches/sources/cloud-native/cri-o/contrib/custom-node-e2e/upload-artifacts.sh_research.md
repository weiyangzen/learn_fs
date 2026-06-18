# sources/cloud-native/cri-o/contrib/custom-node-e2e/upload-artifacts.sh

Purpose: upload CRI-O bundle artifacts and branch/tag marker files to a Google Cloud Storage bucket for custom node e2e testing.

Important APIs and control flow: reads optional `GCS_SA_PATH` and `GCS_BUCKET_NAME` with default bucket `cri-o`. If a service account path is set, activates it with `gcloud`. It uploads `build/bundle/*.tar.gz*` to `$BUCKET/artifacts` with `gsutil -m cp -n`, computes marker from current branch or tag, writes the current commit or exact tag into `latest-$MARKER.txt`, and uploads that marker.

State and persistence: writes local latest marker file and remote GCS artifacts/marker objects.

Dependencies and integration: used by `create-ignition-config.sh`; depends on git, gsutil, optional gcloud, and bundle files created by `make bundle`.

Risks: detached HEAD assumes an exact tag and derives marker from characters 2-5 of the tag, which is version-format dependent. `cp -n` avoids overwriting bundles, so stale artifacts can persist.

Test signals: GCS upload success and marker contents matching expected commit or tag.
