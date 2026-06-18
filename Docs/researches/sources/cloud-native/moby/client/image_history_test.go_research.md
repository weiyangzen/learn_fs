<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_test.go -->
# sources/cloud-native/moby/client/image_history_test.go

Purpose: tests `ImageHistory` error mapping, route construction, option handling, and decode behavior.

Important coverage: daemon internal errors, successful `GET /images/{id}/history`, decoded history items, and platform option query/version behavior where applicable.

Control flow and dependencies: uses mock JSON responses and request assertions.

State and risks: no persistence. The test protects an image read endpoint and its newer platform option path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_test.go -->
