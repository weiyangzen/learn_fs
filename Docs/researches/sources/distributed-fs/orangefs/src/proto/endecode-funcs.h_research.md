<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.h -->
# sources/distributed-fs/orangefs/src/proto/endecode-funcs.h

## Purpose
Defines the macro framework used to generate OrangeFS wire encode/decode functions near protocol type declarations. It covers primitive endian conversion, string/keyval layout, decode allocation helpers, fixed-field struct encoders, array-bearing struct encoders, and enum-union dispatch.

## Important APIs, Types, and Functions
Primitive macros include `encode_uint64_t`, `decode_uint64_t`, `encode_int64_t`, `decode_int64_t`, `encode_uint32_t`, `decode_uint32_t`, `encode_int32_t`, `decode_int32_t`, `encode_char`, `decode_char`, `encode_skip4`, `decode_skip4`, `encode_string`, `decode_string`, `encode_here_string`, `decode_here_string`, `encode_PVFS_ds_keyval`, and `decode_PVFS_ds_keyval`. Structure-generation macros range from `endecode_fields_1` through larger fixed-field forms and specialized array forms such as `endecode_fields_1a`, `endecode_fields_2aa_struct`, `endecode_fields_4aaa_struct`, `endecode_fields_3a2a_struct`, and `endecode_fields_5aa_struct`. It also defines `decode_malloc`, `decode_free`, `DEFINE_STATIC_ENDECODE_FUNCS`, and `encode_enum_union_2_struct`.

## Control Flow
Generated encoders write fields in declared order and advance a `char **` cursor. Generated decoders read fields in the same order, allocate arrays based on decoded counts, and advance the cursor. String decoding points into the encoded buffer instead of allocating, while `decode_here_string` copies into existing struct storage. Array forms encode count fields first, then loop through arrays, sometimes aligning to 8-byte boundaries.

## State and Persistence
No persistent state exists. The macros define a wire format and transient decode allocations. Because decoded strings/keyvals can alias the input buffer, the receive buffer lifetime is part of decoded state.

## Dependencies and Integration Points
Included by generated stubs and protocol headers such as `pvfs2-attr.h`. It depends on BMI byte-order helpers, `roundup8`/`align8` availability from included stubs or surrounding headers, C compiler support for `typeof` outside Windows, and consistent protocol version management.

## Risks
This file is protocol-critical: any field-order or alignment change must update `PVFS2_PROTO_VERSION`. Most decoders trust decoded counts before allocation, so malformed or hostile input can request huge allocations unless upstream size checks constrain it. String size-check macro uses `strlen(*pbuf) + 5`, while actual encoding rounds to 8, so max-size callers must include padding elsewhere. Some macros allocate zero-count arrays differently from later special forms, which can affect release code.

## Test Signals
Round-trip primitive, string, keyval, fixed-field, and array-bearing structs; fuzz decode counts and lengths; run alignment tests on strict-alignment architectures; verify `PVFS2_PROTO_VERSION` changes when generated wire layout changes; and memory-check all decode/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.h -->
