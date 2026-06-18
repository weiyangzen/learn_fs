# sources/cloud-native/moby/releases/versions.yaml

Purpose: release metadata declaring Docker version channels for Moby release automation.

APIs and structure: YAML root `docker` contains `last` set to `29.5.3` and `next` set to `29.6.0`.

State and persistence: this is durable repository release state, not runtime code.

Integration points: likely consumed by release scripts or CI jobs that need current and upcoming Docker version numbers.

Risks and tests: stale values can misdrive release automation. No tests are attached in the listed file set; validation is schema/consumer dependent.
