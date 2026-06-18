<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/assemble_test.go

Purpose: unit test for full BeeMsg assembly and disassembly.

Important APIs/types/functions: `TestAssembleBeeMsg` uses the package-local `testMsg` from `io_test.go`.

Control flow: creates a message with fields and feature flags, assembles it, verifies header detection, disassembles into a new value, then mutates the buffer by appending or truncating data and expects disassembly errors.

State and persistence: in-memory byte buffers only.

Dependencies and integration points: depends on `msg.IsSerializedHeader` and the shared `testMsg` serializer/deserializer. It validates feature-flag propagation through header backfill and body deserialization.

Risks: no coverage for wrong message ID, non-pointer target, header corruption, or body serialization failures.

Test signals: useful transport-level smoke test for exact-buffer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble_test.go -->
