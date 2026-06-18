# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_sh_mask.h

Purpose: generated AMD MP 11.0.8-specific shift/mask header for SMN mailbox, interrupt, counter, and extended scratch registers. It tells consumers how to pack fields for the offsets in `mp_11_0_8_offset.h`.

Important APIs and state: most `MP0_SMN_C2PMSG_*` and `MP1_SMN_C2PMSG_*` registers have a full 32-bit `CONTENT` mask at shift `0`. `MP*_SMN_IH_CREDIT` uses `CREDIT_VALUE` bits `0..1` and `CLIENT_ID` bits `16..23`. For 11.0.8 SMN software interrupts, `MP*_SMN_IH_SW_INT` uses `ID` bits `0..7` and `VALID` bit 8, and `MP*_SMN_IH_SW_INT_CTRL` uses `INT_MASK` bit 0 and `INT_ACK` bit 8. `MP1_SMN_FPS_CNT` and `MP1_SMN_EXT_SCRATCH0..7` are full-width `COUNT`/`DATA` fields.

Control flow: no executable control flow. These constants are used by register-field helpers and low-level firmware interface code when extracting mailbox payloads, setting software interrupt masks, acknowledging interrupt events, or interpreting MP1 scratch values. The file is narrower than the generic MP 11.0 mask header and focuses on the SMN names used by the 11.0.8 PSP path.

State and persistence: stateless macro definitions. The described registers carry volatile hardware state: firmware command payloads, response data, interrupt mask/ack state, interrupt credits, FPS counters, and extended firmware scratch values. Firmware may update these registers asynchronously, so readers must expect change between accesses.

Dependencies and integration: protected by `_mp_11_0_8_SH_MASK_HEADER` and logically paired with `mp_11_0_8_offset.h`. Although the 11.0.8 PSP file in this tree includes only the offset header directly, these masks provide the companion field contract for code that needs `REG_SET_FIELD`/`REG_GET_FIELD` style access to the same registers.

Risks and test signals: the interrupt field layout differs from MP 10.0 SMN software interrupt macros, where `VALID` is bit 0 and `ID` starts at bit 1. Reusing the wrong generation's mask would corrupt interrupt programming. Test signals include field-helper compile coverage, SMN interrupt enable/ack behavior, firmware command/response integrity, and any diagnostics that read the MP1 extended scratch registers.
