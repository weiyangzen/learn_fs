# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.c

## Purpose
`wx_mbx.c` implements the PF/VF mailbox transport used by WangXun SR-IOV devices. It provides lock, read, write, acknowledgment, reset detection, and posted-message polling helpers for both PF-to-VF and VF-to-PF directions.

## Important APIs, types, and functions
PF-side exports are `wx_write_mbx_pf`, `wx_read_mbx_pf`, `wx_check_for_rst_pf`, `wx_check_for_msg_pf`, and `wx_check_for_ack_pf`. VF-side exports are `wx_read_posted_mbx`, `wx_write_posted_mbx`, `wx_check_for_rst_vf`, `wx_check_for_msg_vf`, `wx_read_mbx_vf`, `wx_write_mbx_vf`, and `wx_init_mbx_params_vf`. Internal helpers acquire PF/VF ownership bits, read and cache VF mailbox cause bits, poll for ack/message completion, and clear interrupt cause registers.

## Control flow and behavior
PF write validates size, obtains PF ownership of the VF mailbox, clears stale msg/ack causes, writes dwords into `WX_PXMBMEM(vf)`, mirrors status in the final mailbox word, and sets `WX_PXMAILBOX_STS` to interrupt the VF. PF read obtains the same lock, copies mailbox dwords, mirrors ACK, and writes `WX_PXMAILBOX_ACK`. VF write obtains VFU ownership, clears stale PF status/ack bits, writes `WX_VXMBMEM`, and writes `WX_VXMAILBOX_REQ` to notify PF. VF read obtains the lock, copies `WX_VXMBMEM`, and writes `WX_VXMAILBOX_ACK`. Posted helpers add polling for message or ack using `mbx->udelay` and `mbx->timeout`.

## State and persistence
Mailbox state is split between hardware mailbox registers and `wx->mbx`. `wx->mbx.size`, `mailbox`, `udelay`, and `timeout` define VF transport parameters. `wx->mbx.mailbox` caches PF-to-VF bits so read-clear semantics do not lose reset/status/ack events before the driver consumes them. VF initialization allocates one `vf_data_storage` object and initializes mailbox limits.

## Dependencies and integration points
The file depends on `wx_type.h` register accessors and `wx_mbx.h` constants. It is used by SR-IOV PF code handling VF requests and by VF code negotiating/resetting with the PF. It also interacts with `wx_vf`/`wx_sriov` logic through message IDs declared in the header.

## Risks and edge cases
Mailbox lock acquisition retries only five times, so transient contention can surface as `-EBUSY`. PF operations trust the caller's VF index to address valid mailbox registers. Size handling differs by direction: writes reject oversize messages, reads truncate to mailbox size. Lost or stale ACK/STS bits can break request/response sequencing if callers do not check returns. Posted polling uses atomic polling and fixed microsecond delays; firmware or PF stalls become timeouts. `wx_init_mbx_params_vf()` allocates `vfinfo`, so teardown must free it elsewhere.

## Test signals
SR-IOV tests should cover VF reset notification, API negotiation, VF MAC/VLAN/multicast messages, PF notifications, posted writes with ACK, posted reads after PF status, oversize message rejection, mailbox contention, and PF reset while a VF is polling. Useful signals are absence of mailbox timeout logs, correct ACK/REQ interrupt cause clearing, and stable VF recovery after PF reset.
