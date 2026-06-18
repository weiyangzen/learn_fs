# sources/distributed-fs/beegfs-go/common/beegfs/entity_test.go

## Purpose
This Go test suite validates numeric ID parsing and the `EntityIdParser` behavior over legacy IDs, aliases, and UIDs.

## Important Tests
`TestIdFromString` checks valid 16-bit IDs and rejects zero and overflow. `TestEntityParser` accepts node-type prefixes, trims spaces, handles case, parses aliases and UIDs, and rejects unsupported node types, invalid aliases, invalid IDs, and malformed UIDs. `TestEntityParserWithFixedNodeType` verifies that a bare integer is accepted when exactly one node type is configured.

## Dependencies and Integration
Tests use `stretchr/testify/assert` and cover parser behavior defined across `entity.go`, `entityparser.go`, and `nodetype.go`.

## Signals and Gaps
The suite provides strong coverage for CLI-facing parsing. It does not test `EntityIdSetFromProto`, protobuf conversion round trips, `EntityIdSliceParser`, pflag wrappers, or colon strings with more than two fields.
