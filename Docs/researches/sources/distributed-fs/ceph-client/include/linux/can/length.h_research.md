## sources/distributed-fs/ceph-client/include/linux/can/length.h

**Purpose:** This header calculates Classical CAN and CAN FD frame wire lengths and provides DLC/length conversion helpers.

**Important APIs/types/functions:** It defines bit counts for standard/extended CAN and CAN FD headers, CRC fields, footers, and intermission. Macros include `can_bitstuffing_len()`, `can_frame_bits()`, `can_frame_bytes()`, `CAN_FRAME_LEN_MAX`, `CANFD_FRAME_LEN_MAX`, and `can_cc_dlc2len()`. Inline helpers handle Classical CAN raw DLC (`can_get_cc_dlc()`, `can_frame_set_cc_len()`) and FD sanitization. External APIs are `can_fd_dlc2len()`, `can_fd_len2dlc()`, and `can_skb_get_frame_len()`.

**Control flow, state, persistence:** Macro calculations are pure arithmetic. Classical CAN raw DLC handling conditionally preserves `len8_dlc` only when ctrlmode allows it. No persistent state is stored here.

**Dependencies/integration:** Depends on CAN UAPI frame layouts, CAN netlink ctrlmode, math helpers, and SKBs. Used by drivers and statistics paths that estimate bus load or validate frame sizes.

**Risks and test signals:** Risks include passing unsanitized `data_len`, confusing RTR actual data length with DLC, FD CRC17/CRC21 threshold errors, and bitstuffing worst-case assumptions. Test signals include known frame-length vectors, DLC round trips, SKB length tests for CAN/CAN FD/CAN XL, and busload calculations compared with analyzer measurements.
