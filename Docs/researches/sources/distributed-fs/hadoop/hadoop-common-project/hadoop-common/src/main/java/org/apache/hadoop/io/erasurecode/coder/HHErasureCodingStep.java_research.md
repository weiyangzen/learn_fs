# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHErasureCodingStep.java

Purpose: abstract base for Hitchhiker coding steps, adding HH-specific sub-packetization and shared block storage.

Important APIs and control flow: constructor stores input/output blocks. `getSubPacketSize()` returns fixed value 2. Getters expose blocks. `finish()` is currently a no-op.

State and persistence: stores input/output block arrays and a constant sub-packet size. No persistence.

Dependencies and integration: extended by HH-XOR encoding/decoding steps. The fixed sub-packet size drives expected chunk array shapes.

Risks and test signals: test HH chunk array sizing as `numUnits * 2`. If future HH variants need different sub-packet sizes, this constant becomes a compatibility point.
