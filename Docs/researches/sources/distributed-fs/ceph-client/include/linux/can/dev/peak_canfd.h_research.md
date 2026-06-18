## sources/distributed-fs/ceph-client/include/linux/can/dev/peak_canfd.h

**Purpose:** This header defines the PEAK System uCAN protocol command and message layouts used by PEAK CAN FD capable adapters.

**Important APIs/types/functions:** It enumerates command opcodes (`PUCAN_CMD_*`), received/transmitted message types (`PUCAN_MSG_*`), command structs for reset/mode/timing/filter/abort/error-count/options, message structs for RX/TX/error/status/busload, and many field masks. Inline helpers extract command opcode, build opcode/channel fields, and read channel/DLC/status bits from little-endian packed protocol messages.

**Control flow, state, persistence:** The header models firmware wire-format state. Drivers build packed commands, send them to hardware/firmware, parse incoming message collections, and translate status/error bits into CAN stack state. Persistent device configuration such as filters and timing lives in adapter firmware after commands are accepted.

**Dependencies/integration:** Depends on endian helpers and packed layout rules. Integrated by PEAK USB/PCI drivers with CAN core, bittiming, and SKB translation.

**Risks and test signals:** Risks include packed-struct alignment, endian mistakes, opcode/channel bit overlap, DLC conversion errors, and firmware version drift. Test signals include bus analyzer traces, hardware loopback, FD/bitrate-switch frames, status/error injection, filter programming validation, and sparse endian checks.
