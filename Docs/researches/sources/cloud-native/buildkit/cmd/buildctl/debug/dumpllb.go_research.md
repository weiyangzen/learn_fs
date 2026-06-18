# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpllb.go

Purpose: implements `buildctl debug dump-llb`, a daemonless diagnostic command for decoding serialized LLB definitions into JSON lines or Graphviz DOT.

Important APIs and flow: `dumpLLB` reads from a named file or stdin, calls `loadLLB`, and either JSON-encodes each `llbOp` or writes DOT. `loadLLB` uses `llb.ReadFrom`, unmarshals each protobuf op, computes its digest, and attaches metadata. `writeDot` emits nodes and dependency edges, using mount destinations as edge labels for exec ops. `attr` maps op kinds to readable labels and DOT shapes.

State and dependencies: no persistence; input is an LLB stream and output is stdout. Dependencies include LLB serialization, solver protobufs, OCI digest, JSON, and DOT-compatible formatting.

Risks and test signals: DOT labels are derived from op fields and do not include full metadata; unknown ops fall back to digest labels. Malformed protobufs fail during load. No direct tests are listed, but the command is isolated enough for future golden tests.
