# sources/cloud-native/moby/integration-cli/docker_cli_search_test.go

## Purpose

`docker_cli_search_test.go` defines `DockerCLISearchSuite`, the integration test suite for `docker search`. It validates CLI search behavior against the central registry, including basic query results, filter validation, official/automated/star filters, no-trunc handling, dash-containing queries, and result limits.

Unlike the other files in this work item, this suite depends directly on external registry behavior and network availability. It primarily protects user-facing CLI parsing and daemon/registry search result formatting.

## Important APIs, Types, and Helpers

The primary type is `DockerCLISearchSuite`, with teardown and timeout delegated to `DockerSuite`. Tests use `cli.DockerCmd` for successful search invocations and `dockerCmdWithError` for invalid filters or invalid limits. Assertions use `gotest.tools/v3/assert` and standard `strings`/`fmt` helpers.

No local helper functions are defined in this file. The important contract is the CLI output shape: header plus result rows separated by newlines, result rows starting with repository names, and error output containing "invalid filter" for malformed filter values.

## Control Flow and Coverage

`TestSearchOnCentralRegistry` searches for `busybox` and expects the output to contain the known description "Busybox base image." `TestSearchStarsOptionWithWrongParameter` sends malformed values for `stars`, `is-automated`, and `is-official` through both long and short filter flags, expecting errors and "invalid filter" text.

`TestSearchCmdOptions` compares unfiltered `busybox` output against filtered results. It asserts that `is-official=false` excludes the official `busybox` row, `is-official=true` returns exactly header, one row, and trailing newline, `stars=10` returns no more rows than the unfiltered result, and combined `is-automated`, `stars`, and `--no-trunc=true` are accepted.

`TestSearchOnCentralRegistryWithDash` verifies that a query ending in a dash (`ubuntu-`) is accepted. `TestSearchWithLimit` checks valid limits of 10, 50, and 100 by counting output lines as `limit + 2`; it also checks that limit 101 errors. The negative limit case is skipped by `continue` with a FIXME because daemon validation did not reject `--limit=-1` consistently.

## State and Persistence Behavior

The search suite does not create daemon objects, images, containers, or local files. State is external and transient: results come from the central registry and can change over time. The only persistent behavior under test is CLI/daemon handling of request parameters and output formatting.

## Dependencies and Integration Points

The tests integrate Docker CLI search parsing, daemon registry search API handling, network access, Docker Hub/central registry search behavior, and formatted CLI output. They assume `busybox` remains an official image with stable enough description text and that search result ordering/counts are predictable for the chosen filters and limits.

## Risks and Maintenance Notes

This is a high-flakiness area because it depends on live registry data, external network connectivity, rate limits, service availability, and mutable search ranking or descriptions. Exact line-count assertions for limits assume the registry returns at least the requested number of rows for `docker`, and exact description checks assume Docker Hub metadata stays stable.

Filter validation tests are less dependent on registry data and provide stronger local signal. The skipped negative-limit validation documents a known mismatch between expected range errors and daemon behavior.

## Test Signals

Passing tests signal that `docker search` can reach the central registry, parse and reject invalid filters, apply official/star/automated filters, preserve output shape for filtered results, accept dash-containing queries, and enforce upper result-limit bounds.
