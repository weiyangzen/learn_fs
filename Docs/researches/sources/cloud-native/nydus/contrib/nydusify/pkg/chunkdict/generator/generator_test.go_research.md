# sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator_test.go

Purpose: tests chunkdict generator construction and helper paths with mocked parser/provider/backend behavior.

Important APIs and flow: tests use `gomonkey` to patch external-heavy functions such as remote/parser creation, parser parsing, bootstrap pulling, provider pulls/pushes, and content store operations. They validate `New`, source output for Nydus images, errors for non-Nydus inputs, output JSON/blob handling, `getPushWriter` already-exists behavior, and the `store.Info` descriptor fallback.

State and persistence: uses temporary directories, local content stores, tar/gzip helpers, and mocked readers. It avoids real registries and real `nydus-image`.

Dependencies and integration: covers interfaces to parser, provider, content store, backend, and OCI JSON helpers, giving regression signal for generator orchestration without full network execution.

Risks and test signals: extensive monkey patching isolates units but can hide integration breakage in actual containerd/registry paths. Tests emphasize success/error plumbing over validating generated chunk dictionary semantics.
