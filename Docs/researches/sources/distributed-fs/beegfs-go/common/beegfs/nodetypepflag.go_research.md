# sources/distributed-fs/beegfs-go/common/beegfs/nodetypepflag.go

## Purpose
`NodeTypePFlag` adapts BeeGFS node type parsing to Cobra/pflag command-line flags.

## APIs and Control Flow
`NewNodeTypePFlag` stores a destination pointer and accepted node types. `Type` returns `nodeType`. `String` returns the current node type string when non-invalid, otherwise an empty string. `Set` parses the input with `NodeTypeFromString`, writes the result to the destination pointer, then validates the parsed value against the accepted list and returns a formatted error on mismatch.

## State, Dependencies, and Integration
State is a caller-owned pointer plus accepted values. It integrates with CLI command flag registration.

## Risks and Test Signals
`Set` writes the parsed value before validation, so after an invalid input the destination pointer contains the invalid or unacceptable node type. It assumes `into` is non-nil. Error messages have a trailing comma and space. No direct tests are listed.
