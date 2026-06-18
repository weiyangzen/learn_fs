# sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service.go

## Purpose
Maintains Docker Registry v2 layer metadata mapping uncompressed DiffIDs to compressed blob digests/source repositories, including credential-scoped HMAC tags.

## APIs, Control Flow, and Integration
`V2MetadataService` supports metadata lookup by DiffID, DiffID lookup by digest, add, HMAC tag-and-add, and remove. `V2Metadata` stores digest, source repo, and HMAC. HMAC helpers derive a key from selected auth fields and hash digest+source repository. `Add` deduplicates entries, appends newest, caps per DiffID to 50, stores JSON under `v2metadata-by-diffid`, and stores reverse digest mapping. `Remove` uses reverse mapping, removes matching metadata, and deletes the DiffID record if empty.

## State, Dependencies, and Risks
Persistence uses the metadata store. A nil store makes add/remove no-ops but read operations error. Risks include reverse digest mapping pointing to only the latest DiffID, remove failing if reverse mapping is missing, HMAC compatibility with auth-field changes, and stale metadata influencing push mount/existence behavior. Tests cover add/get/capping/reverse overwrite.
