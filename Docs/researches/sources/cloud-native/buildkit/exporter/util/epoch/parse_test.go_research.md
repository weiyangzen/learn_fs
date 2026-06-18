# sources/cloud-native/buildkit/exporter/util/epoch/parse_test.go

Purpose: unit-tests `ParseBuildArgs` behavior for frontend build-arg forwarding of `SOURCE_DATE_EPOCH`.

Important test cases: numeric strings are accepted and returned; symbolic value `context` is rejected from exporter forwarding; empty string is accepted as a valid exporter override.

Control flow and state: the test is table-like but explicit, runs in parallel, and calls only pure parser logic with in-memory maps.

Dependencies and integration: validates the contract between the Dockerfile frontend, which may support symbolic `SOURCE_DATE_EPOCH` sources, and exporters, which should only receive numeric or empty values.

Risks and test signals: protects against accidentally forwarding symbolic frontend-only values into exporter parsers, and against breaking empty override behavior.
