# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_tcb.h

## Purpose

`t4_tcb.h` defines bit positions, word indices, masks, and value macros for fields in the Chelsio TCP Control Block (TCB). The TCB is firmware/ASIC connection state for TOE/offload connections. This header lets driver code build CPL TCB get/set commands and interpret or modify specific connection fields without hard-coding word offsets.

## Important APIs, Types, and Constants

- TCB word/field macros follow the pattern `TCB_<FIELD>_W`, `_S`, `_M`, and `_V(x)` for word index, shift, mask, and encoded value.
- Link/source fields include `TCB_L2T_IX`, `TCB_SMAC_SEL`, and `TCB_RSS_INFO`.
- `TCB_T_FLAGS` covers a full 64-bit TCB flag word; `TCB_FIELD_COOKIE_TFLAG` identifies a cookie value associated with T-flags operations.
- TCP state and timing fields include `TCB_T_STATE`, `TCB_TIMESTAMP`, `TCB_RTT_TS_RECENT_AGE`, and `TCB_T_RTSEQ_RECENT`.
- Sequence/window fields include `TCB_TX_MAX`, `TCB_SND_UNA_RAW`, `TCB_SND_NXT_RAW`, `TCB_SND_MAX_RAW`, `TCB_RCV_NXT`, and `TCB_RCV_WND`.
- RX/PDU and buffer fields include raw fragment word constants, `TCB_PDU_HDR_LEN_W`, `TCB_RQ_START`, and `TF_RX_PDU_OUT`.
- T-flag bit shifts include `TF_DROP_S`, `TF_DIRECT_STEER_S`, `TF_LPBK_S`, `TF_CCTRL_ECE_S`, `TF_CCTRL_CWR_S`, `TF_CCTRL_RFR_S`, `TF_CORE_BYPASS_S`, and `TF_NON_OFFLOAD_S`.
- Flag helper macros provide `_V(x)` and `_F` forms for boolean flags such as `TF_CORE_BYPASS_F` and `TF_NON_OFFLOAD_F`.

## Control Flow and State Behavior

The file has no executable control flow. It participates in runtime flows when the driver sends `CPL_GET_TCB`, `CPL_SET_TCB_FIELD`, or core TCB-field messages defined in `t4_msg.h`. A caller chooses the TCB word, mask, and value from this header, sends the CPL command to firmware/hardware, and later handles the reply or observes changed connection behavior.

The state addressed by these macros is persistent connection state inside the adapter TCB memory for the life of an offloaded connection. This header does not store state locally, but its constants determine which hardware state is read or mutated.

## Dependencies and Integration Points

- Uses `__u64` in several macros but does not include a type header itself; includers must already have Linux types available.
- Integrates tightly with `t4_msg.h` TCB commands, especially `struct cpl_get_tcb`, `struct cpl_set_tcb_field`, `TCB_WORD_V()`, and cookie/status handling.
- Used by connection management, filter/direct-steering, loopback, congestion-control, non-offload/core-bypass, DDP/PDU, and diagnostics code that needs to inspect or alter adapter connection state.
- Complements `t4_hw.h` `TCB_SIZE` and `t4_regs.h` TP/LE/offload register definitions.

## Risks and Edge Cases

- TCB word/shift/mask values are ABI-sensitive. A wrong offset can modify the wrong connection state and create hard-to-debug traffic corruption or connection teardown.
- The header contains a duplicate definition block for `TCB_T_FLAGS_*`; it is identical, but future edits must keep duplicate definitions synchronized or remove duplication carefully.
- Several `_V(x)` macros do not cast to `__u64`, while fields are 64-bit; callers passing narrow or signed values should ensure correct width before shifting.
- No `_G(x)` getters are provided for most fields; decode paths need to apply shifts/masks manually or add helpers consistently.
- Generation-specific TCB layout differences, if any are introduced elsewhere, must be reflected here with explicit new macros rather than overloading existing names.

## Test Signals

- Compile coverage of all TCB operations catches missing type dependencies and macro spelling issues.
- TOE/offload connection tests validating direct steering, drop, loopback, non-offload, congestion-control, window, and sequence behavior provide functional coverage.
- TCB dump/debug tests can compare decoded fields against firmware/hardware expectations.
- Negative tests should verify that invalid masks/words are rejected by firmware or handled cleanly by the driver.
