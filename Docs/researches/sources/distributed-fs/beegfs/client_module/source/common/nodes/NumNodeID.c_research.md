<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NumNodeID.c -->
## sources/distributed-fs/beegfs/client_module/source/common/nodes/NumNodeID.c

**Purpose:** Implements wire serialization for numeric node IDs. **APIs/functions:** `NumNodeID_serialize` writes the `uint32_t value`; `NumNodeID_deserialize` reads it into an output object and returns false on buffer failure. **Control flow/state:** no ownership or persistence beyond the serialized numeric value; zero convention is interpreted by higher layers. **Dependencies/integration:** uses the common serialization toolkit and is embedded in `EntryInfo`, target mappings, and peer messages. **Risks/tests:** cross-component compatibility depends on keeping the width and endian conversion in `Serialization` stable; tests should round-trip zero, normal, and max IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NumNodeID.c -->
