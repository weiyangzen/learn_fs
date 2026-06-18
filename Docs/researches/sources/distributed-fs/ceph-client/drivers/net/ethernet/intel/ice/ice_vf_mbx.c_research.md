# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.c

## Purpose
Implements PF-to-VF mailbox send support, hardware-link-speed conversion for virtchnl, and malicious/asynchronous VF mailbox message detection. It supports both software snapshot accounting and newer E830 hardware mailbox counters.

## Important APIs and Functions
- `ice_aq_send_msg_to_vf()` builds the `ice_mbx_opc_send_msg_to_vf` admin queue descriptor, writes opcode/status into cookies, and sends optional payload through `hw->mailboxq`.
- `ice_conv_link_speed_to_virtchnl()` returns Mbps for advanced link support or legacy `VIRTCHNL_LINK_SPEED_*` enums otherwise.
- `ice_mbx_vf_state_handler()` is the entry point for software malicious VF detection over a static mailbox snapshot.
- `ice_mbx_vf_dec_trig_e830()` and `ice_mbx_vf_clear_cnt_e830()` manipulate E830 mailbox in-flight counters.
- `ice_mbx_clear_malvf()`, `ice_mbx_init_vf_info()`, and `ice_mbx_init_snapshot()` initialize or clear per-VF and global snapshot state.

## Control Flow
The software detector operates as a state machine over `ICE_MAL_VF_DETECT_STATE_NEW_SNAPSHOT`, `TRAVERSE`, and `DETECT`. A new snapshot clears per-VF message counts, captures mailbox head/tail from the control queue, and chooses detect mode if pending ARQ entries exceed the async watermark. Detect mode increments `vf_info->msg_count`; reaching `ICE_ASYNC_VF_MSG_THRESHOLD` marks the VF malicious once. Traversal advances through the circular queue until the static snapshot or maximum processed-message budget ends.

## State and Persistence
`hw->mbx_snapshot` stores snapshot traversal counters and the list of `ice_mbx_vf_info` records. Each VF record stores `msg_count` and a one-shot `malicious` flag until cleared on VF reset. On E830, hardware counters are cleared/decremented via registers instead of relying solely on software tracking.

## Dependencies and Integration Points
Depends on `ice_common.h`, `ice_vf_mbx.h`, admin/control queue structures, mailbox registers, virtchnl link speed constants, and VF reset paths that clear mailbox state. Virtchnl message handlers use `ice_aq_send_msg_to_vf()` to return responses and events.

## Risks
- `ice_conv_link_speed_to_virtchnl()` uses `fls(link_speed) - 1`; callers should not pass zero unless they accept an unknown/edge result.
- Watermark and max-message parameters are validated; wrong caller values return `-EINVAL` and disable detection for that pass.
- The software detector reports a malicious VF only once until reset, so monitoring must understand the latch.
- Snapshot queue traversal relies on circular queue masks and current `next_to_clean` consistency.

## Test Signals
Test PF-to-VF response delivery with and without payload, legacy and advanced link speed reporting, mailbox floods below and above the 63-message threshold, invalid watermark/max values, reset clearing malicious state, and E830 counter clear/decrement paths.
