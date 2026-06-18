# sources/distributed-fs/ceph-client/include/soc/qcom/tcs.h

Purpose: defines Qualcomm Trigger Command Set request structures and Bus Clock Manager command packing used by RPMh clients.

Important APIs/types/functions: defines `MAX_RPMH_PAYLOAD`, `enum rpmh_state`, `struct tcs_cmd`, `struct tcs_request`, BCM field masks, and `BCM_TCS_CMD(commit, valid, vote_x, vote_y)` built with `u32_encode_bits()`.

Control flow: clients build `struct tcs_cmd` arrays, optionally wrap them in `struct tcs_request`, then submit through RPMh APIs or RSC internals. The `wait` flag has specific meaning for active-only batch writes, while `rpmh_write()` and async writes impose their own completion semantics.

State and persistence: structures are request descriptors. Persistent effects occur in RPMh resources after commands are accepted by hardware.

Dependencies and integration: depends on `linux/bitfield.h` and `linux/bits.h`. Included by RPMh core, RPMh RSC, BCM interconnect voter, clock/regulator/power-domain drivers, and Adreno GMU/HFI code.

Risks: exceeding `MAX_RPMH_PAYLOAD`, bad address encoding, or incorrect wait semantics can fail requests or deadlock callers. BCM vote packing must preserve valid/commit bits and X/Y vote widths. Test signals include interconnect bandwidth votes, RPMh batch writes, active/sleep/wake state transitions, and compile-time checks for users of the structs.
