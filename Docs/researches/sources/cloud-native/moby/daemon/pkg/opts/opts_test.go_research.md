<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/opts_test.go

## Purpose
Tests generic option containers and validators in `opts.go`.

## Important APIs, Types, And Functions
Tests cover `ValidateIPAddress`, `MapOpts`, `ListOpts`, `ValidateDNSSearch`, `ValidateLabel`, named wrappers, `ParseLink`, and `MapMapOpts`.

## Control Flow
Table-driven validators assert normalized output or exact errors. Container tests mutate shared slices/maps and inspect length, lookup, deletion, and nested key assignment.

## State, Dependencies, And Integration Points
No persistent state. It depends on `gotest.tools` assertions and protects shared daemon flag infrastructure.

## Risks And Test Signals
The tests explicitly allow duplicate list values and check map de-duplication through `GetMap`. They cover reserved label namespaces, IPv6 normalization, DNS length/shape, legacy link parsing, validator invocation, and nested map syntax. `MemBytes` is not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts_test.go -->
