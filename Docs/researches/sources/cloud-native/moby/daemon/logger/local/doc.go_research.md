# sources/cloud-native/moby/daemon/logger/local/doc.go

Purpose: documents the local logging driver and its record format.

Important APIs/types/functions: no runtime symbols.

Control flow/state/persistence: describes each message as protobuf bytes wrapped by big-endian uint32 header and footer to support efficient forward and reverse reading.

Dependencies/integration: matches implementation in `local.go` and `local/read.go`.

Risks: documentation must stay aligned with the persistent disk format.

Test signals: none directly.
