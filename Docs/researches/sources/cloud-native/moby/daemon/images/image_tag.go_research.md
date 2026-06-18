<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_tag.go -->
# sources/cloud-native/moby/daemon/images/image_tag.go

Purpose: adds or updates a repository tag for an image.

Important APIs and control flow: `TagImage` calls `referenceStore.AddTag` with force enabled, updates the image's last-updated time, and logs a tag event with the familiar tag name.

State and persistence: writes reference store mappings and image metadata; emits an event.

Dependencies and integration: used by import, load, build export, and API tag flows. It depends on distribution references and image-store timestamp support.

Risks: if `SetLastUpdated` fails after the tag is added, the reference mutation remains but the call returns an error. Forced tag replacement can move existing tags.

Test signals: no direct tests here; tag API tests and import/load/build tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_tag.go -->
