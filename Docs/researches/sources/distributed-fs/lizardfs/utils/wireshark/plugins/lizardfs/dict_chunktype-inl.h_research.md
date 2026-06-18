# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_chunktype-inl.h

Purpose: generated/static value-string include fragment for Wireshark display of LizardFS chunk type values.

Important data: maps `0` to `standard`, then encodes XOR parity and data-part chunk types for levels 2 through 10. Values follow the formula used elsewhere in LizardFS: parity at `(max_xor_level + 1) * level`, data parts immediately after parity.

Control flow/state: data-only include intended to be placed inside a `value_string` array. It does not include header guards because it is an inline initializer fragment.

Dependencies/integration: included by `make_dissector.py` generated code as `dict_chunktype-inl.h` for the external dictionary field `chunktype`.

Risks and test signals: risks are drift from core `ChunkType` numeric assignments and missing future erasure/replication formats. Test signals are generated dissector compile, correct display of standard and XOR chunk names in packet Info and tree columns, and alignment with `chunk_converter.cc` header byte 20 values.
