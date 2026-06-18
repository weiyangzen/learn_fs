# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.h

## Purpose
`fm10k_mbx.h` defines the mailbox ABI used by the fm10k driver. It describes PF/VF mailbox registers, VF mailbox registers, switch-manager FIFO layout, header field encodings, mailbox states, error codes, buffer sizing, operation callbacks, FIFO state, and the exported initialization prototypes.

## Important APIs, types, and functions
The file defines register macros such as `FM10K_MBMEM()`, `FM10K_MBMEM_VF()`, `FM10K_MBMEM_SM()`, `FM10K_MBMEM_PF()`, `FM10K_MBX()`, `FM10K_MBICR()`, `FM10K_GMBX`, `FM10K_VFMBX`, and `FM10K_VFMBMEM()`. It also defines mailbox interrupt/control bits including `FM10K_MBX_REQ`, `FM10K_MBX_ACK`, request/ack interrupt bits, interrupt enable/disable bits, and global request/ack interrupt bits.

The key type definitions are `enum fm10k_mbx_state`, `enum fm10k_msg_type`, `struct fm10k_mbx_ops`, `struct fm10k_mbx_fifo`, and `struct fm10k_mbx_info`. `struct fm10k_mbx_ops` is the driver-facing operation table for connect, disconnect, readiness checks, enqueue, process, and handler registration. `struct fm10k_mbx_info` is the complete runtime state container used by `fm10k_mbx.c`.

Header field helpers `FM10K_MSG_HDR_FIELD_SET()` and `FM10K_MSG_HDR_FIELD_GET()` encode and decode PF/VF and SM mailbox header fields. Exported initialization prototypes are `fm10k_pfvf_mbx_init()` and `fm10k_sm_mbx_init()`.

## Control flow
This header does not execute code, but it defines the control contract followed by `fm10k_mbx.c`. The PF/VF state machine is documented as CLOSED -> CONNECT -> OPEN -> DISCONNECT -> CLOSED, with transitions caused by local `connect()`/`disconnect()` calls and remote CONNECT, DATA, DISCONNECT, or ERROR headers. The header format carries type, tail, head, reserved bits, and either CRC, connect size, or error number.

The switch-manager contract defines a pair of hardware FIFOs with a header containing local tail, version, remote head, and error. Version 0 represents reset/negotiation, and `FM10K_SM_MBX_VERSION` represents the supported active protocol.

## State and persistence behavior
The header codifies volatile runtime state rather than durable state. `struct fm10k_mbx_info` stores FIFO buffers, indexes, state, CRC/version fields, timeout configuration, last test result, message counters, and a fixed in-struct buffer sized by `FM10K_MBX_BUFFER_SIZE`. This state is recreated during mailbox initialization and reset flows.

Mailbox buffer sizing constants define capacity and message limits: Tx FIFO is 512 DWORDs, Rx FIFO is 128 DWORDs, and maximum message size is constrained by both. VF mailbox memory size and MTU are smaller (`FM10K_VFMBMEM_LEN`, `FM10K_VFMBX_MSG_MTU`) and influence connect-size validation.

## Dependencies and integration points
The header includes `fm10k_type.h` and `fm10k_tlv.h`, so it is tied to hardware type declarations and TLV message handling. It is included by common hardware code and mailbox implementation code, and its operation table is consumed by PCI, netdev, IOV, and MAC/VLAN paths through `hw->mbx.ops`.

The error-code range is intentionally outside common Linux errno values, using visible `0xFE**` encodings when embedded in mailbox messages. This makes local software errors and remote mailbox protocol errors share a compact transport representation.

## Risks and edge cases
Changing any shift, size, register, or buffer constant would affect the hardware ABI. The code relies on FIFO sizes being powers of two for mask arithmetic, and on invalid PF/VF mailbox index values 0 and all-ones being reserved. The documented state machine matters because the implementation intentionally ignores or resets on some messages depending on state.

The SM FIFO length is derived from the XOR distance between PF and SM mailbox memory regions; mistakes in these constants could make the SM path overwrite or read from the wrong hardware mailbox area. Error-code collisions with Linux errno values are avoided by convention, so new errors should stay inside the documented mailbox range.

## Test signals
Useful validation includes compile-time coverage of all users after header changes, mailbox connect/data/disconnect cycles for both PF/VF and SM paths, tests of `FIELD_SET`/`FIELD_GET` round trips for all defined fields, and protocol fault tests for reserved indexes, reserved bits, invalid sizes, unsupported SM versions, and expected error-code propagation.
