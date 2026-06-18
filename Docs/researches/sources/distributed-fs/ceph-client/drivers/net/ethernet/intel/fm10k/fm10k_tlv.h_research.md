# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.h

## Purpose
Defines the fm10k mailbox TLV header format, type system, parser result limits, attribute schema structures, handler table structures, typed put/get wrappers, parser entry points, and test-message IDs. It is the shared declaration layer for the TLV implementation and PF/VF mailbox users.

## Important APIs, Types, and Functions
Key macros define ID, flags, and length bit positions, `FM10K_TLV_HDR_LEN`, aligned-length calculation, dword count calculation, `FM10K_TLV_RESULTS_MAX`, and the sentinel `FM10K_TLV_ERROR`. `enum fm10k_tlv_type` covers null strings, MAC addresses, booleans, unsigned/signed integers, little-endian structs, and nested attributes. `struct fm10k_tlv_attr` describes legal attributes, and `struct fm10k_msg_data` maps message IDs to attribute schemas and handler callbacks. Declaration macros such as `FM10K_TLV_ATTR_U32`, `FM10K_TLV_ATTR_LE_STRUCT`, `FM10K_MSG_HANDLER`, `FM10K_TLV_MSG_TEST_HANDLER`, and `FM10K_TLV_MSG_ERROR_HANDLER` reduce table boilerplate.

## Control Flow
The header has no runtime control flow, but it controls TLV dispatch contracts. Message handlers receive an array of attribute pointers indexed by attribute ID, and callers use the typed wrappers to encode/decode values using fixed lengths. The message and attribute arrays must be sentinel-terminated for the parser's linear search behavior.

## State and Persistence Behavior
The header defines the persistent TLV wire format. A TLV header stores byte length excluding the header, a message flag when the item is a top-level message, and a 16-bit type/ID. It also defines the maximum parser result array size of 32, meaning mailbox protocols with attribute IDs above 31 are rejected by this parser unless handled outside the normal result array.

## Dependencies and Integration Points
Includes `fm10k_type.h` after a forward declaration for `struct fm10k_msg_data`. It is included by `fm10k_tlv.c`, `fm10k_pf.h`, `fm10k_vf.h`, and mailbox-related code that registers handlers or emits TLVs.

## Risks
The macros encode ABI assumptions in bit shifts and alignment; any change affects every mailbox protocol user. Attribute IDs must stay within `FM10K_TLV_RESULTS_MAX` for parsed results. The include chain depends on `fm10k_type.h` for `struct fm10k_hw` and `struct fm10k_mbx_info`, so circular header changes can break compilation. Signed integer wrappers reuse the same raw value function as unsigned wrappers, so consumers must pass correctly typed storage.

## Test Signals
Compile all PF/VF mailbox users, static checks of TLV header length/dword macros, parser tests for all declared `enum fm10k_tlv_type` values, attribute IDs at 0 and 31, ID 32 rejection, sorted and unsorted handler schema behavior, unknown-message fallback, and the built-in test handler are useful signals.
