# sources/distributed-fs/beegfs-go/common/beegfs/consistencystateparser.go

## Purpose
`ConsistencyStateParser` constrains string parsing of consistency states to an accepted set for command-line or API input validation.

## APIs and Control Flow
`NewConsistencyStateParser` defaults accepted states to `Good`, `NeedsResync`, and `Bad` when none are supplied. `Parse` converts input with `ConsistencyStateFromString`, checks whether the result is in the parser's accepted list, and returns a formatted error listing accepted values otherwise.

## State, Dependencies, and Integration
The parser is a slice of accepted `ConsistencyState` values. It uses `strings.Builder` and `fmt` for diagnostics. It integrates with CLI flag or command validation where not every state is allowed.

## Risks and Test Signals
Error messages append accepted values with a trailing comma and space. Empty accepted lists cannot represent "accept none" because construction defaults to all real states. There is no listed direct unit test.
