<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/config.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/config.go

Purpose: JSON config structs for test dockerd daemon configuration.

Important APIs and types: `Config`, `BuilderConfig`, and `BuilderEntitlements`.

Control flow: no functions; struct tags define JSON output for features, registry mirrors, and builder entitlements.

State and persistence: values are marshaled by test setup elsewhere.

Dependencies and integration: used by dockerd integration helpers and BuildKit builder tests.

Risks: `BuilderConfig.Entitlements` has no explicit json tag, so default field name is used unless Go JSON lowercasing is acceptable for the target config.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/config.go -->
