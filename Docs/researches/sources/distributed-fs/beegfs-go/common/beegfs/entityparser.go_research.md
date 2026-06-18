# sources/distributed-fs/beegfs-go/common/beegfs/entityparser.go

## Purpose
`EntityIdParser` converts user input into one of BeeGFS's supported entity identity forms: UID, legacy node-type ID, bare numeric ID for a fixed node type, or alias.

## APIs and Control Flow
`NewEntityIdParser` stores ID bit size and accepted node types, defaulting to client, meta, storage, and management. `Parse` trims input. If a colon is present, it splits on `:`, treats `uid:<id>` as signed 64-bit UID greater than zero, otherwise parses `<nodeType>:<id>` and validates the node type against accepted values. Without a colon, it first tries alias validation, then tries a bare numeric ID only when exactly one node type is accepted. `EntityIdSliceParser` splits comma-separated input and parses each element with an embedded parser.

## State, Dependencies, and Integration
Parser state is immutable after construction. It integrates with pflag wrappers and CLI commands that need flexible entity identifiers.

## Risks and Test Signals
The colon path uses `strings.Split` and only reads the first two fields, so `a:b:c` is treated like `a:b` rather than rejected for extra components. For fixed node types, alias parsing wins before bare numeric parsing; numeric aliases are invalid, so the fallback works for numbers. Tests cover many normal and invalid cases but not extra-colon input or slice parsing.
