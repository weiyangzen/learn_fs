## sources/cloud-native/containers-storage/pkg/idtools/parser.go

Purpose: parses CLI/config ID map triplets into `IDMap` slices.

Important APIs/types/functions: `parseTriple` and `ParseIDMap`.

Control flow: each non-empty map spec is split on `:`, must contain a multiple of three fields, each triple parses as uint32 container ID, host ID, and size, then converts to int with an extra guard on 32-bit builds.

State and persistence: pure parsing; no filesystem or global state.

Dependencies and integration points: used where user-provided uidmap/gidmap strings configure namespace mappings.

Risks: all parse failures collapse to the same standard malformed error, so details are hidden. Multiple triplets can be packed into one string, which callers must understand. Does not validate overlap or zero size.

Test signals: `parser_test.go` covers valid maps, malformed numbers, oversized values, and wrong field counts.
