<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_test.go -->
# sources/cloud-native/moby/client/container_create_test.go

Purpose: tests the container create wrapper’s validation, route construction, body encoding, query handling, and capability normalization.

Important coverage: daemon internal errors, image-not-found mapping, `name` query, AutoRemove in host config, connection failure classification, and canonical capability output for add/drop lists including duplicate and `ALL` handling.

Control flow and dependencies: mock callbacks inspect request path and decode the JSON body. Tests use container API structs and gotest assertions.

State and risks: no persistent state. This suite protects one of the highest-impact wrapper methods because create request encoding affects container lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_test.go -->
