# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.h

Purpose: Declares the LiquidIO mailbox protocol shared by PF and VF code.

Important APIs, types, and functions: The header defines mailbox command IDs (`OCTEON_VF_ACTIVE`, `OCTEON_VF_FLR_REQUEST`, `OCTEON_PF_CHANGED_VF_MACADDR`, `OCTEON_GET_VF_STATS`), handshake sentinels (`OCTEON_PFVFACK`, `OCTEON_PFVFSIG`, `OCTEON_PFVFERR`), transfer limits, and wait constants. `union octeon_mbox_message` packs type, response-needed bit, command, length, and six parameter bytes into a 64-bit first word. `struct octeon_mbox_cmd` stores header, up to 32 data words, queue number, receive length/status, and callback. `struct octeon_mbox` owns the lock, queue number, state, hardware register pointers, and in-flight request/response buffers.

Control flow: Users build `struct octeon_mbox_cmd`, call `octeon_mbox_write()`, and later process completed responses through `octeon_mbox_read()` plus `octeon_mbox_process_message()`. Request handlers reuse the same command object to send responses when needed.

State and persistence: State is explicit bitmask state in `enum octeon_mbox_state`. It is volatile driver state backed by memory-mapped mailbox registers.

Dependencies and integration: Depends on `struct octeon_device`, `struct cavium_wk`, and `struct oct_vf_stats` from surrounding LiquidIO headers. It forms the PF/VF control plane used by CN23XX SR-IOV support.

Risks: Message `len` must be bounded to `OCTEON_MBOX_DATA_MAX`; callers must respect request vs response state rules. Bitfield layout and endian assumptions matter because the first word is exchanged with firmware/peer function.

Test signals: Validate packed header fields, max-length transfers, request-without-response cleanup, response callback status, and state transitions after error and cancel paths.
