<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.h

## Purpose
Defines firmware communication constants, queue/message data structures, inline command helpers, and public RCFW channel APIs for the `bng_re` driver.

## Important APIs, Types, And Functions
- Constants define BAR regions, offsets, command queue trigger value, CREQ/CMDQ depths and entry sizes, doorbell sizes, command cookie mask, and blocking-command bit.
- `struct bng_fw_cmdqe` models a 16-byte command queue entry; `struct bng_re_crsbe` models a 1024-byte response side buffer.
- `bng_fw_cmdqe_npages()` and `bng_fw_cmdqe_page_size()` compute memory required for CMDQ depth.
- `struct bng_re_cmdq_mbox`, `bng_re_cmdq_ctx`, `bng_re_creq_db`, `bng_re_creq_ctx`, `bng_re_crsqe`, `bng_re_rcfw_sbuf`, `bng_re_rcfw`, and `bng_re_cmdqmsg` define mailbox, queue, completion, shadow-entry, side-buffer, channel, and message state.
- `bng_re_rcfw_cmd_prep()` initializes opcode and command size in a `cmdq_base`.
- `bng_re_fill_cmdqmsg()` fills a command message wrapper.
- `bng_re_get_cmd_slots()` and `bng_re_set_cmd_slots()` handle normal and TLV-encoded command sizing.
- Public prototypes expose allocation, enable/disable, IRQ start/stop, message send, firmware init, and firmware deinit.

## Control Flow
The header's inline helpers are used before command submission. Callers prepare a command with byte size, calculate required slots, then `bng_re_set_cmd_slots()` converts the command size field to firmware slot units for non-TLV commands or byte length for TLV commands. The public functions are implemented in `bng_fw.c` and are called by `bng_dev.c` and slow-path modules.

## State And Persistence
The declared structures persist channel state for the life of the RDMA device. The shadow response table tracks outstanding command cookies, response buffers, request size, free slots at submission, opcode, and waiter liveness. Flags on the command context persist firmware initialization, stall detection, and first-doorbell behavior.

## Dependencies And Integration Points
Includes `bng_tlv.h` for TLV detection and uses command/event structures and bit definitions from `bng_roce_hsi.h` through implementation includes. It relies on `bng_res.h` types such as `bng_re_hwq`, `bng_re_reg_desc`, and `bng_re_db_info`, plus Linux waitqueues, tasklets, spinlocks, PCI DMA addresses, and atomic counters.

## Risks And Edge Cases
`BNG_FW_CREQ_ENTRY_POLL_BUDGET` is defined twice with the same value, which is harmless but noisy. The command slot helpers mutate `req->cmd_size`; callers must not use the original byte size after `bng_re_set_cmd_slots()` unless they retained it separately. TLV commands interpret `total_size` as units in `get` and convert to bytes in `set`, so TLV header correctness is critical. Cookie space is fixed to `BNG_FW_CMDQE_MAX_CNT - 1`, tying outstanding command tracking to CMDQ depth.

## Test Signals
Compile coverage should catch structure/prototype drift. Unit-style tests or debug assertions around command sizing should cover TLV and non-TLV requests at boundary sizes. Runtime firmware command tests validate cookie assignment, side-buffer response addressing, first-doorbell behavior, and CREQ epoch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.h -->
