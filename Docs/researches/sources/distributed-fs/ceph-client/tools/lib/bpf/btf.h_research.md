# sources/distributed-fs/ceph-client/tools/lib/bpf/btf.h

## Purpose
`btf.h` is libbpf's public BTF interface. It declares opaque BTF and BTF.ext object types, section-name constants, creation/parsing/loading APIs, mutation APIs for constructing BTF records, transform APIs for deduplication, relocation and permutation, dump APIs, and inline helpers for interpreting `struct btf_type` payloads.

The header is designed for C and C++ consumers. It keeps the main object layouts opaque while exposing stable accessors and small inline helpers for BTF UAPI record payloads.

## Important APIs, Types, and Functions
Section constants are `BTF_ELF_SEC` for `.BTF`, `BTF_EXT_ELF_SEC` for `.BTF.ext`, `BTF_BASE_ELF_SEC` for `.BTF.base`, and `MAPS_ELF_SEC` for `.maps`.

Opaque declarations include `struct btf`, `struct btf_ext`, `struct btf_type`, and `struct bpf_object`. The public endianness enum is `enum btf_endianness` with little and big endian values.

Creation and parse APIs are `btf__new()`, `btf__new_split()`, `btf__new_empty()`, `btf__new_empty_split()`, `btf__new_empty_opts()`, `btf__parse()`, `btf__parse_split()`, `btf__parse_elf()`, `btf__parse_elf_split()`, `btf__parse_raw()`, and `btf__parse_raw_split()`. `struct btf_new_opts` provides optional base BTF and `add_layout` support.

Kernel and lookup APIs include `btf__load_vmlinux_btf()`, `btf__load_module_btf()`, `btf__load_from_kernel_by_id()`, `btf__load_from_kernel_by_id_split()`, `btf__load_into_kernel()`, `btf__find_by_name()`, `btf__find_by_name_kind()`, `btf__type_cnt()`, `btf__base_btf()`, `btf__type_by_id()`, `btf__fd()`, and `btf__set_fd()`.

Type and string inspection APIs include `btf__pointer_size()`, `btf__set_pointer_size()`, `btf__endianness()`, `btf__set_endianness()`, `btf__resolve_size()`, `btf__resolve_type()`, `btf__align_of()`, `btf__raw_data()`, `btf__name_by_offset()`, and `btf__str_by_offset()`.

`.BTF.ext` APIs include `btf_ext__new()`, `btf_ext__free()`, `btf_ext__raw_data()`, `btf_ext__endianness()`, and `btf_ext__set_endianness()`.

Builder APIs cover strings, type copying, complete BTF appending, primitive types, references, arrays, structs, unions, fields, enums, enum64, forward declarations, typedefs, CVR modifiers, type tags and attributes, functions, function prototypes, parameters, variables, data sections, data-section variable entries, declaration tags, and declaration attributes.

Transform option structs are `struct btf_dedup_opts` with optional `btf_ext` and `force_collisions`, and `struct btf_permute_opts` with optional `btf_ext`. Public transform APIs are `btf__dedup()`, `btf__relocate()`, `btf__permute()`, and `btf__distill_base()`.

Dump APIs declare `struct btf_dump`, `struct btf_dump_opts`, callback type `btf_dump_printf_fn_t`, `btf_dump__new()`, `btf_dump__free()`, `btf_dump__dump_type()`, `btf_dump__emit_type_decl()`, and `btf_dump__dump_type_data()` with their option structs.

Inline helper APIs include kind predicates such as `btf_is_int()`, `btf_is_struct()`, `btf_is_func_proto()`, `btf_is_decl_tag()`, and `btf_is_any_enum()`, compatibility helper `btf_kind_core_compat()`, integer metadata helpers `btf_int_encoding()`, `btf_int_offset()`, `btf_int_bits()`, payload accessors `btf_array()`, `btf_enum()`, `btf_enum64()`, `btf_members()`, `btf_params()`, `btf_var()`, `btf_var_secinfos()`, `btf_decl_tag()`, and member helpers `btf_member_bit_offset()` and `btf_member_bitfield_size()`.

## Control Flow and Usage Model
Consumers generally create or parse a BTF object, inspect or mutate it through the declared APIs, optionally deduplicate or relocate it, serialize it with `btf__raw_data()`, or load it into the kernel with `btf__load_into_kernel()`. Split-BTF callers pass a base object at creation or parse time, then type and string lookup APIs transparently resolve references through the base.

The builder API is order-sensitive for compound payloads. A caller starts a struct or union with `btf__add_struct()` or `btf__add_union()`, then immediately appends members with `btf__add_field()`. The same pattern applies to enums and enumerators, function prototypes and params, and data sections and variable info.

The header documents libbpf error conventions: most constructors return an error-code-encoded pointer unless strict clean pointers are enabled, while `btf__new_empty_opts()` documents NULL-on-error. Integer APIs return negative error codes and set `errno` through implementation helpers.

The inline helpers are thin views over Linux BTF UAPI memory layout. They assume the caller passes a valid `struct btf_type *` for the expected kind and perform pointer arithmetic to reach payload records immediately after the base type header.

## State and Persistence Behavior
Object lifetime is explicit. `btf__free()` releases a BTF object, and `btf_ext__free()` releases a BTF.ext object. Raw-data pointers returned by `btf__raw_data()` and `btf_ext__raw_data()` are object-owned snapshots and should be treated as invalid after object mutation or free.

`struct btf_new_opts`, `struct btf_dedup_opts`, `struct btf_permute_opts`, and dump option structs use `size_t sz` plus `*_last_field` macros for libbpf's forward/backward-compatible option validation pattern.

Base-BTF state is visible through `btf__base_btf()`, but ownership remains implementation-defined by the creation path. Callers that pass a base BTF must keep it alive as required by the implementation unless ownership is explicitly transferred by a parse path such as embedded `.BTF.base`.

## Dependencies and Integration Points
The header depends on `<linux/btf.h>` and `<linux/types.h>` for UAPI types and records, `<stdbool.h>` and `<stdarg.h>` for public signatures, and `libbpf_common.h` for `LIBBPF_API` and compatibility macros.

It is consumed by libbpf internals such as `btf.c`, BTF dumping code, BPF object loading code, linkers, and external applications that need BTF construction, inspection, CO-RE metadata, or kernel BTF loading.

The header compensates for older kernel headers by defining BTF kind constants that might not be present, including `BTF_KIND_FUNC`, `BTF_KIND_VAR`, `BTF_KIND_FLOAT`, `BTF_KIND_DECL_TAG`, `BTF_KIND_TYPE_TAG`, and `BTF_KIND_ENUM64`.

## Risks and Edge Cases
Inline payload accessors do not validate kind or bounds. Misusing `btf_members()` on a non-composite type, or reading enum64 payloads when the underlying data is too short, is caller error and can read invalid memory.

The `btf_enum64_value()` helper intentionally treats `struct btf_enum64` as a `__u32` array to support older system headers and C++ consumers. This is portable for the expected UAPI layout but depends on the BTF enum64 record staying three 32-bit words.

Several APIs accept type IDs that may reference future types. This is necessary for graph construction but means header-level type safety is weak until validation, dedup, serialization, or kernel loading.

The public API mixes pointer-returning constructors, integer-returning mutators, and object-owned raw pointers. Callers must consistently use `libbpf_get_error()` or check negative returns according to each function's contract.

Option-struct `sz` must be initialized correctly. Uninitialized option structs can be rejected by `OPTS_VALID()` in the implementation.

## Test Signals
Header/API tests should compile the header as C and C++, with both recent and older kernel headers, to verify fallback BTF kind definitions and the enum64 helper.

API contract tests should cover error-pointer constructors, clean-pointer strict mode, option struct sizing, base-BTF construction, split-BTF lookup, raw data ownership expectations, and all builder ordering constraints.

Inline helper tests should cover every BTF kind predicate, modifier grouping in `btf_is_mod()`, enum/enum64 compatibility through `btf_is_any_enum()` and `btf_kind_core_compat()`, bitfield offset and size decoding with and without `kflag`, and payload accessor correctness for arrays, members, params, variables, data sections, and declaration tags.

Integration tests should compile external-style users that include only `btf.h` plus standard dependencies and exercise parse, inspect, mutate, dedup, dump, and load declarations without relying on private `struct btf` or `struct btf_ext` layouts.
