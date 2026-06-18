# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/make_dissector.py

Purpose: Python source generator that parses annotated LizardFS protocol definitions and emits a Wireshark C dissector.

Important APIs/classes: `Types` maps internal integer/string/blob kinds to Wireshark field types, bases, and tvbuff getters. `PacketDissectionVariant` tracks one packet layout variant, with byte positions, variable-length expressions, optional variant condition, and field metadata. Methods such as `add_int_field`, `add_string8_field`, `add_string32_field`, `add_blob_field`, `condition`, `get_info()`, and `print_method()` drive generated C output.

Control flow: stdin is scanned line by line. Packet macros matching `(LIZ_)?(AN|CS|CL|MA|ML|TS)TO...` start new dissections and populate the `type` dictionary. `/// field values: name` blocks build dictionaries. Other `///` lines define packet variants with fields like `name:32`, `NAME`, `STDSTRING`, `STRING[n]`, `BYTES[n]`, and conditional selectors. LIZ messages default to `version == 0` when no condition is present. After parsing, the script prints includes, globals, dictionaries, one C method per variant, dispatch switches by message type, TCP PDU framing, preference registration for ports 9419-9422, and field registration.

State and persistence: no files are directly written; generated C is stdout. Internal dictionaries aggregate type and field metadata, and field type consistency is enforced.

Dependencies/integration: depends on protocol header comments following the expected annotation grammar and on Wireshark C APIs such as `tcp_dissect_pdus`, `proto_tree_add_item`, and preference ranges. External chunk type and goal dictionaries are included by name.

Risks and test signals: generated C is vulnerable to unsanitized field names from comments, and parser errors terminate generation. Some code contains historical typos but is functional. Variable-length fields and unknown variants are key risk areas. Test signals are generation from the current protocol header, C compiler warnings, dissector behavior for fixed/variable payloads, malformed length handling, dictionary display, and large/LIZ packet version dispatch.
