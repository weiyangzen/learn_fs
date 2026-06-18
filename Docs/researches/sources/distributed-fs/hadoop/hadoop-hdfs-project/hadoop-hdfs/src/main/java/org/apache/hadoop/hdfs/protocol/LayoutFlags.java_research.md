# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutFlags.java

Purpose: Defines the feature-flag section protocol for HDFS fsimage/edit layout streams. Current production behavior supports no independent flags and rejects any non-empty feature flag section.

Important APIs and functions: `read(DataInputStream)` reads an int length and requires it to be zero. `write(DataOutputStream)` writes zero. The constructor is private.

Control flow: Reading throws `IOException` for negative lengths or positive lengths, with positive values treated as unsupported flags requiring software upgrade. Writing always emits a zero-length feature flag section.

State and persistence behavior: The only persisted value is the zero integer written to layout streams. No in-memory state is stored.

Dependencies and integration points: Depends on Java data streams. It is tied to layout feature `ADD_LAYOUT_FLAGS` and fsimage/edit log readers/writers.

Risks: Any future feature-flag support must extend this format without breaking old readers. Rejecting positive lengths is deliberate compatibility behavior; changing it changes upgrade semantics. Negative length rejection protects malformed/corrupt input.

Test signals: Tests should read/write zero, reject negative length, reject positive length, and verify fsimage/edit loading behavior around layout versions that include flags.
