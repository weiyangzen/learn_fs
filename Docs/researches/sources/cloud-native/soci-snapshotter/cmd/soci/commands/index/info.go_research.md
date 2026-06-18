## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/info.go

Purpose: implements `soci index info`, printing the raw JSON of a SOCI index artifact.

Important APIs/types/functions: `infoCommand` and `prettyPrintJSON`.

Control flow: parse digest argument, open artifacts DB, verify digest is not a zTOC layer entry, open selected content store, fetch descriptor by digest, read all bytes, and JSON-indent them to stdout.

State and persistence: read-only against DB and content store.

Dependencies and integration: artifacts DB identifies artifact type; selected store fetches bytes; JSON formatting is standard library.

Risks and test signals: missing or malformed digest errors surface directly; large indexes are fully buffered. No direct tests here.
