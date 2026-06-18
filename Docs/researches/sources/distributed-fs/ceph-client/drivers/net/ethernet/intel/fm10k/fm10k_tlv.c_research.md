# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.c

## Purpose
Implements the fm10k mailbox TLV encoder, decoder, validator, dispatcher, default error handler, and a built-in test-message generator/validator. This is the shared protocol layer for PF-to-switch-manager and PF-to-VF mailbox messages.

## Important APIs, Types, and Functions
Message construction starts with `fm10k_tlv_msg_init`, then attributes are appended with `fm10k_tlv_attr_put_mac_vlan`, `fm10k_tlv_attr_put_bool`, `fm10k_tlv_attr_put_value` and typed wrappers, or `fm10k_tlv_attr_put_le_struct`. Attribute extraction uses `fm10k_tlv_attr_get_mac_vlan`, `fm10k_tlv_attr_get_value` and typed wrappers, and `fm10k_tlv_attr_get_le_struct`. Parser internals are `fm10k_tlv_attr_validate`, `fm10k_tlv_attr_parse`, and `fm10k_tlv_msg_parse`. `fm10k_tlv_msg_error` is the default not-implemented handler. Test support is provided by `fm10k_tlv_msg_test_attr`, `fm10k_tlv_msg_test_create`, and `fm10k_tlv_msg_test`.

## Control Flow
Writers initialize a message header with the message flag and ID, append attributes at `FM10K_TLV_DWORD_LEN(*msg)`, encode data in CPU-order dwords, set each attribute length, then grow the message length with 4-byte alignment. The parser first verifies the message flag, extracts the message ID, finds a handler entry by sorted ID, falls back to the error handler entry if no exact match exists, parses attributes into a fixed `results[32]` array according to the handler's attribute schema, then invokes the handler. Attribute parsing validates each header and type/length contract, silently ignores schema-unknown attributes, rejects out-of-range result IDs, and verifies the final parsed byte offset equals the message length. The test handler validates each present attribute against known constants, recursively parses nested attributes, and returns a TLV result message through the mailbox.

## State and Persistence Behavior
There is no global mutable protocol state except static test constants. State is encoded in caller-provided `u32` message buffers and in `results` pointer arrays. Message and attribute headers persist lengths in bytes above bit 20, flags in bits 16-19, and IDs in bits 0-15. Little-endian structs are converted to/from CPU-order dwords when placed in TLVs, which makes the mailbox dword stream host-order while preserving ABI struct endian fields.

## Dependencies and Integration Points
Includes `fm10k_tlv.h`, which includes `fm10k_type.h`; relies on Ethernet address helpers, endian helpers, bit helpers, and mailbox `enqueue_tx` operations through handler callbacks. It is used by PF and VF code to build mailbox requests, parse replies, and register message handlers in `struct fm10k_msg_data` tables.

## Risks
The implementation does not track caller buffer capacity when appending attributes, so callers must size stack buffers correctly. Handler and attribute schema arrays are expected to be sorted by ID and terminated with `FM10K_TLV_ATTR_LAST` or `FM10K_TLV_ERROR`; malformed ordering can produce wrong lookup or out-of-bounds walking. `fm10k_tlv_attr_get_mac_vlan` does not check a non-null VLAN pointer even though callers pass one. Nested attribute support is private and relies on the nested header length being updated through the nest pointer. Length math is packed into header-shifted units, so mistakes in byte-versus-shifted length handling can corrupt parsing.

## Test Signals
Test with every TLV attribute type, minimum and maximum integer sizes, null strings including missing terminator, MAC/VLAN encoding, little-endian struct round trips, nested attributes, unknown attributes, unknown message IDs, malformed message/attribute flags, invalid lengths, result IDs above 31, unaligned struct lengths, buffer-size stress in callers, and mailbox test-message request/reply through PF/VF paths.
