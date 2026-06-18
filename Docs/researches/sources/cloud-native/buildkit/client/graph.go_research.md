# sources/cloud-native/buildkit/client/graph.go

Purpose: client-facing graph/status data structures for solve progress and responses.

Important APIs/types/functions: `Vertex` captures graph vertex digest, inputs, name, timings, cache/error state, and progress group. `VertexStatus` tracks progress counters. `VertexLog` carries stream bytes. `VertexWarning` carries warning text, URL, source info, and ranges. `SolveStatus` groups progress events. `SolveResponse` stores exporter/cache exporter responses.

Control flow: this file contains data definitions only; flow is in clients that populate and consume these structs.

State and persistence: no internal state; JSON tags define serialized API shape.

Dependencies/integration points: `solver/pb` progress/source structures, OpenContainers digest, and solve/status streaming APIs.

Risks/test signals: schema changes are client API changes. No direct tests in this subset; integration is exercised through solve progress consumers.
