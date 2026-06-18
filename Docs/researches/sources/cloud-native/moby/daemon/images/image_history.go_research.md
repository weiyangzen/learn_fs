<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_history.go -->
# sources/cloud-native/moby/daemon/images/image_history.go

Purpose: builds the API image history response from image config history, layers, parents, and tags.

Important APIs and control flow: `ImageHistory` resolves the image, walks config history in order while mapping non-empty history entries to rootfs diff IDs and layer sizes, reverses entries for API output, then walks parent image IDs to fill IDs and tag lists from the reference store. It updates the image `history` metric.

State and persistence: reads image store, layer store, and reference store. No state is mutated.

Dependencies and integration: used by the image history API and depends on rootfs chain reconstruction, layer release discipline, and reference classification.

Risks: malformed images with more non-empty history entries than rootfs diff IDs return an error. Parent lookup failures stop ID/tag enrichment rather than failing the entire response after the current entries have been built.

Test signals: no direct tests in this subset; API history tests cover expected output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_history.go -->
