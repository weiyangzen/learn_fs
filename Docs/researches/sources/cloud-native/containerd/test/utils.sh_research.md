<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/utils.sh -->
# sources/cloud-native/containerd/test/utils.sh

- Purpose: General test utility helpers for GCS log upload and checksums.
- Important functions: `upload_logs_to_gcs`, `create_ttl_bucket`, and `sha256`.
- Control flow: Create bucket if missing, set a 30-day lifecycle rule and public ACL/default ACL, copy logs, and print a gcsweb URL. `sha256` chooses `sha256sum` or `shasum -a256`.
- State and persistence: Creates/updates GCS buckets and lifecycle rules; writes temporary lifecycle JSON locally.
- Dependencies and integration: Requires `gsutil`, GCS credentials, and checksum tools. Used by build/push/report scripts.
- Risks: Public-read ACLs and new buckets are security-sensitive; lifecycle rule is hardcoded to 30 days.
- Test signals: GCS listing/copy success and correct checksum output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/utils.sh -->
