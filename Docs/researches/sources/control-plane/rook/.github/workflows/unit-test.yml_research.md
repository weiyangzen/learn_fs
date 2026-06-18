# sources/control-plane/rook/.github/workflows/unit-test.yml

## Purpose

Runs Rook unit tests and verifies jq-dependent liveness probe tests are not skipped.

## Important APIs, Types, and Functions

The `unittests` job sets up Go 1.26, installs jq through `dcarbone/install-jq-action` using workflow-dispatch input `version` defaulting to `1.7`, exports `ROOK_UNIT_JQ_PATH`, unsets `AZURE_EXTENSION_DIR`, runs `make -j $(nproc) test`, tees output, then greps for a skip message.

## Control Flow

Push, PR, and manual dispatch events trigger the job unless `skip-ci` is present. After tests run, a second step fails if the output indicates the MDS liveness probe jq tests were skipped because jq was unknown.

## State and Persistence Behavior

No repository state persists. Test output is in runner-local `output.txt` and GitHub logs.

## Dependencies and Integration Points

It integrates with Makefile unit tests, Go modules, jq-dependent unit tests, Azure KMS tests affected by `AZURE_EXTENSION_DIR`, and Mergify-required `unittests`.

## Risks and Edge Cases

The grep check assumes exact skip-message text. Manual dispatch can test alternate jq versions. Unsetting `AZURE_EXTENSION_DIR` prevents host runner configuration from influencing unit tests.

## Test Signals

Passing means unit tests completed and jq-backed MDS liveness probe tests actually ran.
