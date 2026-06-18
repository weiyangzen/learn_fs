<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_update_test.go -->
# sources/cloud-native/moby/client/config_update_test.go

Purpose: validates `ConfigUpdate` error and routing behavior.

Important coverage: daemon 500 mapping, invalid empty/whitespace ids, and successful `POST /configs/config_id/update`.

Control flow and dependencies: uses mock clients, `assertRequest`, and `gotest.tools` error assertions.

State and risks: no persistence. The test verifies the update endpoint shape but does not assert the `version` query or encoded spec body in detail.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_update_test.go -->
