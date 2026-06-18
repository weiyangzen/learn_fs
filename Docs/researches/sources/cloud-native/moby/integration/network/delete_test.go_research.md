<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/delete_test.go -->
# sources/cloud-native/moby/integration/network/delete_test.go

Purpose: verifies Docker network create/delete behavior and ambiguity resolution when network names resemble network IDs.

Important APIs/types/functions: `containsNetwork` scans `networktypes.Summary` items by ID. `createAmbiguousNetworks` creates three networks: a normal network, one named with the first network's ID prefix, and one named with the full first network ID. Tests are `TestNetworkCreateDelete` and `TestDockerNetworkDeletePreferID`.

Control flow: create/delete test creates a named network, asserts it appears, removes it by name, and asserts absence. Ambiguity test creates the three networks, removes by the first network's 12-character ID prefix, then removes by full ID, and verifies the full-ID-named network remains while the ID-targeted networks are gone.

State/persistence: creates Docker networks in the daemon and removes them through the API. No file state.

Dependencies/integration: uses package `setupTest`, API client, internal network helpers, gotest assertions, and OS skips for Linux/Windows differences.

Risks: ambiguous name/ID behavior is subtle; changing API lookup precedence can break compatibility. The Windows skip documents shared-network limitations in that environment.

Test signals: passing tests confirm basic network lifecycle and that ID/prefix deletion preference is preserved over same-looking names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/delete_test.go -->
