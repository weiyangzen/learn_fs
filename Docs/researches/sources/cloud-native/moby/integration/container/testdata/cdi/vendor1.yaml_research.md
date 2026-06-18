# sources/cloud-native/moby/integration/container/testdata/cdi/vendor1.yaml

Purpose: Static CDI vendor spec fixture defining one injectable device for CDI-related container integration tests outside this work item.

Important structure: The YAML declares `cdiVersion: "0.3.0"`, `kind: "vendor1.com/device"`, and one device named `foo`. Its `containerEdits.env` adds `FOO=injected`.

State and dependencies: It is read as test data by CDI tests and has no runtime behavior by itself. It depends on CDI spec directory discovery and parser support for version 0.3.0.

Risks and signals: It is intentionally small but important for testing device discovery and environment injection. Schema drift, invalid kind/name fields, or env edit changes would alter CDI test expectations.
