<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_test.go -->
# sources/cloud-native/moby/client/client_test.go

Purpose: tests central `Client` behavior: construction, env configuration, API path formatting, host URL parsing, version negotiation, connection failures, and redirect policy.

Important coverage: `TestNewClientWithNilOpt`, env-based client construction, `TestGetAPIPath`, `TestParseHostURL`, default version setting, negotiation with lower/equal/higher daemon versions, invalid/too-old versions, negotiation override behavior, automatic negotiation with empty/fixed versions, connection failure mapping, and `CheckRedirect`.

Control flow and dependencies: tests use mock transports and synthetic ping responses to drive `Client.checkVersion` and `negotiateAPIVersion`. Host parsing tests cover Unix sockets, Windows named pipes, TCP hosts, and invalid forms.

State and integration behavior: no persistent state; environment variables are scoped to tests. The tests protect all endpoint wrappers because every wrapper uses `getAPIPath`, negotiation, host setup, and redirect handling.

Risks and test signals: primary risks are incorrect version prefixing, silently using unsupported daemon API versions, unexpected redirect following for non-GET requests, and losing connection-failed classification. This suite is high-signal because many endpoint tests rely on this shared core.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_test.go -->
