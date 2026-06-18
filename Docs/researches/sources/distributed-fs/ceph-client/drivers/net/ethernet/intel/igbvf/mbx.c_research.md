# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.c

## Purpose
`mbx.c` implements the VF side of the PF/VF mailbox protocol. It provides posted read/write operations, polling for PF acknowledgements or messages, read-to-clear bit preservation, mailbox lock acquisition, and initialization of `hw->mbx.ops`.

## Important APIs, Types, And Functions
The exported function is `e1000_init_mbx_params_vf()`. Important internal operations include `e1000_poll_for_msg()`, `e1000_poll_for_ack()`, `e1000_read_posted_mbx()`, `e1000_write_posted_mbx()`, `e1000_read_v2p_mailbox()`, `e1000_check_for_bit_vf()`, `e1000_check_for_msg_vf()`, `e1000_check_for_ack_vf()`, `e1000_check_for_rst_vf()`, `e1000_obtain_mbx_lock_vf()`, `e1000_write_mbx_vf()`, and `e1000_read_mbx_vf()`.

## Control Flow
Posted writes call the raw write op, then poll until PFACK or timeout. Posted reads poll until PFSTS, then read mailbox memory. Raw writes first obtain VF ownership via `V2PMAILBOX.VFU`, clear stale ACK/message bits, copy up to `size` words into `VMBMEM`, update counters, and signal PF with `REQ`. Raw reads acquire ownership, copy words out, acknowledge with `ACK`, and update receive counters.

## State And Persistence
State is kept in `hw->mbx`: timeout, delay, mailbox size, operation pointers, and statistics. Read-to-clear V2P bits are cached in `hw->dev_spec.vf.v2p_mailbox` so a status bit is not lost when multiple checks inspect the register. Timeout is set to zero after polling failure, causing future posted sends to fail until reset reinitializes mailbox communication.

## Dependencies And Integration Points
The file depends on register wrappers from `regs.h`, mailbox constants from `mbx.h`, `udelay()`, and `hw->mbx_lock` held by callers. `vf.c` uses the ops to request reset, MAC/VLAN/multicast/filter changes, LPE changes, and link-status communication with the PF.

## Risks
Mailbox operations are race-prone because PF and VF share the buffer and status bits are read-to-clear. Callers must hold `hw->mbx_lock`; lockdep assertions enforce this for raw read/write. Timeout zeroing can make a VF appear permanently unable to communicate until reset. Message size is not internally bounded beyond caller-supplied `size`, so callers must respect `E1000_VFMAILBOX_SIZE`.

## Test Signals
Validate VF reset handshake, MAC address programming, VLAN add/remove, multicast updates, link checks, and PF reset notifications. Useful counters are `msgs_tx`, `msgs_rx`, `acks`, `reqs`, and `rsts`; timeout paths should be tested with PF unavailable.
