# sources/distributed-fs/ceph-client/include/uapi/linux/target_core_user.h

## Purpose
Defines the TCMU userspace target ABI for SCSI command processing through an mmaped UIO region, command ring, mailbox, and generic netlink events.

## Important APIs, Types, and Constants
`TCMU_VERSION`, `TCMU_MAILBOX_VERSION`, and mailbox capability flags describe supported features. `struct tcmu_mailbox` carries command ring offset/size, `cmd_head`, and user-updated `cmd_tail`. `enum tcmu_opcode` names `TCMU_OP_PAD`, `TCMU_OP_CMD`, and `TCMU_OP_TMR`. `struct tcmu_cmd_entry_hdr` packs length and opcode in `len_op` and carries command IDs and flags. Inline helpers get/set op and length. `struct tcmu_cmd_entry` contains request CDB/data offsets or response status/read length/sense. `struct tcmu_tmr_entry` carries task management requests. Generic netlink command and attribute enums report device add/remove/reconfig and features.

## Control Flow, State, and Persistence
Kernel writes ring entries and advances `cmd_head`, then notifies userspace through UIO. Userspace processes entries, writes response fields, and advances `cmd_tail`; optional capabilities allow out-of-order completion, read length, TMR, and buffer retention. Device configuration is delivered over generic netlink.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/uio.h>`, and `__DECLARE_FLEX_ARRAY`. Integrates with LIO target core, UIO mmap/interrupts, SCSI userspace backstores, and generic netlink management.

## Risks and Test Signals
Risks include ring wrap/pad handling, memory ordering, packed flexible layouts, length/op bit corruption, and userspace failing to advance `cmd_tail`. Test ring wrap, PAD entries, command and TMR processing, sense buffer propagation, feature negotiation, and concurrent reset/removal events.
