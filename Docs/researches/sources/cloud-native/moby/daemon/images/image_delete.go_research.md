<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_delete.go -->
# sources/cloud-native/moby/daemon/images/image_delete.go

Purpose: implements image and reference deletion semantics for the legacy image service.

Important APIs and control flow: `ImageDelete` resolves a ref/ID, handles optional single-platform validation, removes repository references first when a named ref was supplied, cleans up related digest refs, and then calls `imageDeleteHelper`. `isSingleReference` determines whether all refs are one repository with at most one tag. `removeImageRef` and `removeAllReferencesToImageID` manipulate refstore entries and append API delete records. `imageDeleteHelper` enforces hard and soft conflicts, deletes the image store entry, records layer deletions, logs events, and optionally prunes parents quietly. `checkImageDeleteConflict` checks child images, running containers, stopped containers, and active references.

State and persistence: mutates reference store entries, image store records, layer metadata through image-store delete, and event logs. It reads container store and image ancestry state.

Dependencies and integration: used by API image remove and image prune. It integrates API delete responses, event metrics, container store filters, image/reference/layer stores, platform-aware `GetImage`, and daemon error typing.

Risks: deletion semantics differ for named references and ID prefixes, and `force` only overrides soft conflicts. The conflict checks include normal container `ImageID` use and image mounts in one early branch, but later stopped/running conflict helpers only check `ImageID`. Quiet pruning deliberately suppresses some conflicts, so callers must inspect returned records rather than assume full ancestry deletion.

Test signals: no direct tests in this file; prune, remove, and container-use integration tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_delete.go -->
