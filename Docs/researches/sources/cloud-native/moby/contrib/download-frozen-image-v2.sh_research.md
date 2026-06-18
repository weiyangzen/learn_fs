# sources/cloud-native/moby/contrib/download-frozen-image-v2.sh

## Purpose
Downloads Docker Registry v2 image manifests and blobs into a frozen archive layout for CI and educational use.

## APIs, Types, And Functions
Important helpers include `usage`, `fetch_blob`, `handle_single_manifest_v2`, `get_target_arch`, and `get_target_variant`. The script depends on `curl`, `jq`, registry auth tokens, manifest lists, schema v2 manifests, and Bash arrays.

## Control Flow, State, And Integration
The script validates tools, parses target directory and image references, obtains registry tokens, fetches manifests and blobs, handles architecture/variant selection, writes layer/config files, and assembles repository/tag metadata unless disabled. Persistent state is the frozen image directory tree and temporary tag files.

## Risks And Test Signals
Risks include registry API drift, auth failures, digest mismatch, Bash version portability, platform selection mistakes, and partial downloads. Integration is with Docker Hub registry APIs and CI fixtures that need pre-fetched images.
