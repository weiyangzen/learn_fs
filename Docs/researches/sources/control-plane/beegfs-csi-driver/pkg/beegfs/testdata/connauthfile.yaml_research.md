# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile.yaml

Purpose: Minimal raw connAuth fixture for `parseConnAuthFromFile`.

Important data: One list entry maps `sysMgmtdHost: 127.0.0.0` to `connAuth: secret1` with no explicit encoding, which is treated as raw.

Control flow: Parser appends a newline for raw/empty encoding and either updates an existing filesystem-specific config for the host or appends a new one.

State and persistence: Static test fixture. No writes.

Dependencies and integration points: Feeds tests for raw auth and combined TLS cert merging. The resulting `ConnAuth` is later written by `writeClientFiles` to `connAuthFile` with mode `0400`.

Risks: The implicit newline is intentional but can surprise users comparing literal YAML value to generated file content. The fixture only covers one host and no explicit `encoding: raw` spelling.

Test signals: Confirms raw connAuth defaults and host matching/append behavior.
