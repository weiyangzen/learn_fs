# sources/cloud-native/ostree/tests/test-commit-timestamp.sh

Purpose: verifies explicit and reproducible commit timestamp inputs.

Important APIs/functions: `ostree commit --timestamp='@1234567890'`, `ostree show`, environment `SOURCE_DATE_EPOCH`, and error assertions for invalid/overflowing values.

Control flow: initializes `testrepo`, commits with a CLI timestamp and checks displayed date, commits with `SOURCE_DATE_EPOCH`, verifies invalid and overflowing environment values fail, and confirms the valid environment timestamp appears in `show`.

State/persistence: writes commits to `testrepo` and captures show/error output files. Dependencies include stable UTC date formatting.

Integration/risk/test signals: protects reproducible build timestamp behavior and input validation. Risks are date formatting changes and platform-specific overflow wording, handled with an alternation regex. Two TAP cases cover CLI and environment timestamps.
