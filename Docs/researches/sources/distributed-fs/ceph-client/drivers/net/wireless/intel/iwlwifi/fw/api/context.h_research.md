# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/context.h

Purpose: Defines common firmware context ID/color encoding and add/modify/remove actions for PHY, MAC, binding, and related context commands.

Important APIs and types: `enum iwl_ctxt_id_and_color` defines ID and color bit positions/masks plus invalid values. `FW_CMD_ID_AND_COLOR()` packs IDs and colors. `enum iwl_ctxt_action` defines invalid, add, modify, and remove operations. `IWL_LMAC_24G_INDEX` and `IWL_LMAC_5G_INDEX` identify LMAC roles.

Control flow: Header-only packing definitions are used when constructing context-related host commands.

State and persistence: No state. Encoded values identify firmware runtime objects and are often used to prevent stale references after object recreation.

Dependencies and integration points: Consumed by binding, MAC, PHY, station, and security key context APIs across MVM/MLD and firmware context management.

Risks: ID/color packing assumes 8-bit fields. Newer firmware may use `FW_CTXT_ID_INVALID` without color, so callers must choose the invalid representation by firmware generation. Wrong action values can leak or destroy firmware contexts.

Test signals: Pack/unpack context IDs/colors, add/modify/remove lifecycle for MAC/PHY/binding contexts, invalid context handling on old and new firmware, and dual-LMAC context placement.
