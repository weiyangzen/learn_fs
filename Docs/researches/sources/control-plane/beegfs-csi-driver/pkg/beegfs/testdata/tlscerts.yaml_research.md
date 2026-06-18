# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/tlscerts.yaml

Purpose: Minimal TLS certificate fixture for `parseTLSCertsFromFile`.

Important data: One list entry maps `sysMgmtdHost: 127.0.0.0` to `tlsCert: "cert1"`.

Control flow: Parser appends a newline to the cert value and writes it into a matching or new filesystem-specific config. Unlike connAuth, there is no encoding field in this fixture.

State and persistence: Static fixture.

Dependencies and integration points: The parsed `TLSCert` is later written by `writeClientFiles` to the per-volume TLS cert path with mode `0400`, but not inserted into `beegfs-client.conf`.

Risks: Only the simplest cert value is covered; multiline PEM-style certs are not represented here. Automatic newline addition must match how BeeGFS client expects cert file content.

Test signals: Used in `TestParseConnAuthAndTLSCertsFromFiles` to verify TLS cert append/merge behavior alongside connAuth.
