<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/push.sh -->
# sources/cloud-native/containerd/test/push.sh

- Purpose: Uploads containerd test release tarballs and checksums to a Google Cloud Storage bucket.
- Important variables: `DEPLOY_BUCKET`, `DEPLOY_DIR`, `BUILD_DIR`, `TARBALL`, `LATEST`, `PUSH_VERSION`, and `VERSION`.
- Control flow: Verify tarball and checksum exist, create bucket with TTL if missing, derive deploy path, upload files, optionally copy versioned artifacts and latest markers.
- State and persistence: Writes objects into `gs://$DEPLOY_BUCKET/$DEPLOY_DIR` and possibly updates latest/version aliases.
- Dependencies and integration: Requires `gsutil`, sourced `test/utils.sh` for bucket helper/checksum, and GCS credentials.
- Risks: Uploading latest aliases is mutable global state; missing deploy dir defaults can overwrite shared paths.
- Test signals: `gsutil cp` success and public GCS URLs resolving.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/push.sh -->
