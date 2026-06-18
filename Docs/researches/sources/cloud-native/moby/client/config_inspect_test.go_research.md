<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect_test.go -->
# sources/cloud-native/moby/client/config_inspect_test.go

Purpose: tests `ConfigInspect` behavior for missing ids, daemon errors, not-found responses, and successful inspection.

Important coverage: empty and whitespace ids should produce `cerrdefs.IsInvalidArgument`; 404 responses should classify as not found; success expects `GET /configs/config_id` and JSON decoding into a Swarm config.

Control flow and dependencies: uses `WithMockClient`, `errorMock`, `mockJSONResponse`, and `assertRequest`.

State and risks: no persistent state. The tests protect public error contracts and route stability for config inspection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect_test.go -->
