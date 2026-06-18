<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts_test.go

## Purpose
Regression-tests daemon host parsing and `--add-host` validation.

## Important APIs, Types, And Functions
`TestParseDockerDaemonHost` covers full protocol dispatch. `TestParseTCP` isolates TCP default filling and validation. `TestValidateExtraHosts` checks host-to-IP strings.

## Control Flow
Tests are map/table-driven: invalid inputs assert exact error strings and empty address output; valid inputs assert normalized address strings. Extra-host tests verify valid IPv4/IPv6 examples and error substrings for invalid forms.

## State, Dependencies, And Integration Points
No external state. Expected outputs depend on platform constants such as `DefaultHTTPHost`, so Unix and Windows builds differ through companion files.

## Risks And Test Signals
Map iteration order is irrelevant but exact error strings are brittle against Go URL parser wording. Coverage is strong for common daemon bind address confusion, IPv6 brackets, paths, unsupported schemes, and host-gateway-adjacent validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_test.go -->
