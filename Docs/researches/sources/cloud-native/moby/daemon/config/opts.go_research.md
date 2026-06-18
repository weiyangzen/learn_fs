<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/opts.go -->
# sources/cloud-native/moby/daemon/config/opts.go

## Purpose
Parses daemon node generic resource configuration into API swarm generic resources.

## Important APIs, Types, And Functions
`ParseGenericResources` accepts `[]string` and returns `[]swarm.GenericResource`.

## Control Flow
Empty input returns nil. Non-empty input is parsed by swarmkit's generic resource parser, then converted from gRPC objects to API objects.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Integrates daemon config validation with swarmkit generic resources and daemon cluster conversion code. Called by `config.Validate`.

## Risks And Test Signals
Risks are parser error propagation and mixed named/discrete resource semantics. Common config tests assert malformed and mixed resources fail.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/opts.go -->
