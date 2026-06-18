# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.h

## Purpose
This header defines the VF-side PF/VF mailbox protocol ABI, including versions, opcodes, word types, status codes, link enums, timing and buffer limits, the packed mailbox word union, and exported VF mailbox helper APIs.

## Important APIs, Types, And Functions
- Protocol versioning: `enum octep_pfvf_mbox_version` and `OCTEP_PFVF_MBOX_VERSION_CURRENT`.
- Opcodes: version, MTU, MAC, link info, stats, Rx state, link status, device remove, firmware info, offloads, and link notification.
- Status and timing: `OCTEP_PFVF_MBOX_TIMEOUT_WAIT_COUNT`, `OCTEP_PFVF_MBOX_TIMEOUT_WAIT_UDELAY`, retries, max inline data size, and max bulk data buffer.
- Payload ABI: `union octep_pfvf_mbox_word` overlays a 64-bit word with typed views for command data, fragments, version, MAC, MTU, link state/status, firmware info, and offloads.
- Exported helpers: setup/delete, send command, bulk read, version check, set/get MAC, set MTU, set Rx/link state, get link status, device remove, firmware info, and offload setting.

## Control Flow
The union's opcode/type fields let VF code construct a command word and PF code return an ACK/NACK in the same register. Bulk commands use the `s_data` view and the fragment bit. The function prototypes are used by VF main and ethtool code to make PF-backed operations look like local driver operations.

## State And Persistence
The header defines no live storage. It constrains mailbox users through fixed protocol values and payload sizes. Negotiated version and bulk buffers are stored in `struct octep_vf_device` and `struct octep_vf_mbox` from `octep_vf_main.h`.

## Dependencies And Integration Points
The definitions must match PF-side `octep_pfvf_mbox.h`. It is included by `octep_vf_main.h` and implemented by `octep_vf_mbox.c`. The protocol is coupled to PF firmware control operations because PF services most VF commands by proxying to firmware.

## Risks And Edge Cases
- PF and VF headers duplicate enums and union layout; any mismatch breaks ABI.
- `OCTEP_PFVF_MBOX_MAX_DATA_BUF_SIZE` is smaller than the PF header's staged data size, which is a compatibility risk for bulk stats.
- Bitfield ABI and `__packed` layout must remain compiler-compatible across PF/VF builds.
- The timeout delay macro is not directly used by the implementation, which hard-codes `usleep_range(1000, 1500)`.

## Test Signals
Compile PF and VF together, compare opcode/version constants, run mailbox version negotiation, exercise each exported helper with PF ACK and NACK, validate fragmented reads near buffer limits, and test notification decoding.
