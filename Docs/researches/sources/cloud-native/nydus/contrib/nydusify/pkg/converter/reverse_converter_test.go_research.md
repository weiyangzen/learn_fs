# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter_test.go

Purpose: smoke, flow, error, performance, integration, and CI-friendly tests for reverse conversion setup and early failure behavior.

Important fixtures and functions: `MockRemoter` models the remote interface, `checkNydusImageAvailable` and `skipIfNydusImageNotAvailable` gate tool-dependent tests, and `TestHelperProcess` can emulate selected `nydus-image` command behavior.

Control flow: most tests construct `Opt` values and call `ReverseConvert`, asserting that invalid platform strings, bad push retry delays, canceled contexts, unavailable registries, or invalid work dirs produce errors. Registry-backed tests require `NYDUS_TEST_REGISTRY`; tool-backed tests skip if `nydus-image` is absent.

State and persistence: tests use `./tmp` in many cases and rely on ReverseConvert cleanup. Environment variables influence availability, registry selection, and helper process behavior.

Dependencies and integration points: external `nydus-image`, optional registry, containerd content interfaces, testify assertions/mocks.

Risks and test signals: tests are useful for parameter validation but provide limited deterministic coverage of a successful reconversion. Many assertions only require some error, so regressions deeper in manifest conversion or push output could remain undetected without a real integration environment.
