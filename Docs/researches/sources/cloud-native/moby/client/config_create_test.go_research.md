<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_create_test.go -->
# sources/cloud-native/moby/client/config_create_test.go

Purpose: validates `Client.ConfigCreate` error propagation and request routing.

Important coverage: internal-server-error mapping and successful `POST /configs/create` against the mock transport.

Control flow and dependencies: constructs a client with `WithMockClient`, uses `errorMock` or a callback that calls `assertRequest`, then calls `ConfigCreate` with a `ConfigCreateOptions` value.

State, risks, and test signals: no persistent state. The test confirms method/path behavior but does not deeply inspect the encoded `swarm.ConfigSpec` body.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_create_test.go -->
