<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_list.go -->
# sources/cloud-native/moby/daemon/images/image_list.go

Purpose: implements filtered image listing for the legacy image service.

Important APIs and control flow: `Images` validates filters, computes dangling/all image candidates, resolves `before`, `since`, and `until` filters to timestamps, filters labels and references, skips unsupported OS images, calculates layer size, fills tags/digests, applies dangling/reference/all visibility rules, counts containers per image, optionally computes shared layer size across selected/all images, sorts by creation time descending, and returns API summaries. `newImageSummary` initializes summary fields with sentinel shared/container values.

State and persistence: reads image store maps/heads, reference store, layer store, and container store. No state is mutated.

Dependencies and integration: used by `docker images` and API list endpoints. It integrates filter parsing, path glob matching for references, rootfs chain accounting, and container image usage counts.

Risks: list output can skip images whose layer disappears between map and get calls. Shared-size calculation can fail on missing shared layers. Reference matching must compare familiar and canonical forms, and invalid glob patterns surface as errors.

Test signals: no direct tests here; daemon image-list tests usually exercise filter and summary behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_list.go -->
