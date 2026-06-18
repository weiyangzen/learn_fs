# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.c

## Purpose
`fbnic_tlv.c` implements page-sized firmware TLV message construction, attribute extraction, validation, parsing, nested/array support, and a built-in randomized self-test message/parser used to verify TLV mechanics.

## Important APIs, Types, And Functions
Public builders include `fbnic_tlv_msg_alloc()`, flag/value/int/MAC/string put helpers, and nested start/stop helpers. Public readers/parsers include unsigned/signed/string getters, `fbnic_tlv_attr_addr_copy()`, `fbnic_tlv_attr_parse_array()`, `fbnic_tlv_attr_parse()`, `fbnic_tlv_msg_parse()`, and `fbnic_tlv_parser_error()`. Test support includes `fbnic_tlv_test_create()`, `fbnic_tlv_parser_test()`, and `fbnic_tlv_test_index`.

## Control Flow
Messages are allocated as one zeroed page with a message header length in dwords. Attribute put helpers check remaining page space, write an attribute header, copy and pad data, and increase message length by aligned dwords. Nested start creates an attribute whose temporary length is also in dwords; nested stop adds the nested length to the parent and converts the nested header length to bytes.

Parsing first validates that the top header is a message and within one page, selects a parser by message ID, parses attributes using an index, then calls the parser function with a results array. Attribute validation rejects message headers in attribute position, out-of-range IDs, required unknown cannot-ignore attributes, page overrun, bad string termination, bad flag length, oversized ints/binaries, and unaligned nested/array data. Duplicate known attributes are rejected.

## State And Persistence
TLV messages are transient page allocations owned by callers. Parser results point into the original message buffer. The test path keeps a static randomized `test_struct` initialized by `get_random_once()` and compares parsed output against it, including nested and array contents.

## Dependencies And Integration Points
The file depends on byteorder definitions from the header, Linux page allocation, random data, string helpers, Ethernet address sizes, and firmware message definitions elsewhere. Firmware mailbox modules use this TLV API to encode and decode host/firmware messages.

## Risks
Length units differ between message headers (dwords) and attribute headers (bytes), with nested attributes temporarily using dwords until closed. Misuse can corrupt later attributes or trigger parser rejection. Results arrays are indexed by TLV ID and capped at 32; adding attributes with larger IDs requires design changes. `cannot_ignore` unknown attributes fail parsing, so firmware/driver version skew must be handled intentionally.

## Test Signals
The built-in test message/parser exercises unsigned/signed integer sizing, MAC copying, flags, strings, arrays, nested attributes, and duplicate/invalid parsing behavior. Additional useful tests include page-full ENOSPC, unterminated string rejection, cannot-ignore unknown rejection, duplicate attribute rejection, and array overflow handling.
