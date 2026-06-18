# sources/distributed-fs/ceph-client/tools/include/uapi/linux/btf.h

Purpose: defines the on-wire/on-disk BPF Type Format metadata ABI used by the kernel, BPF loaders, debuggers, and CO-RE tooling. It describes BTF headers, type records, string offsets, kind encodings, and trailing records for complex type kinds.

Important APIs/types: key structures are `btf_header`, `btf_layout`, `btf_type`, `btf_enum`, `btf_array`, `btf_member`, `btf_param`, `btf_var`, `btf_var_secinfo`, `btf_decl_tag`, and `btf_enum64`. Macros extract packed fields from `btf_type.info` (`BTF_INFO_KIND`, `BTF_INFO_VLEN`, `BTF_INFO_KFLAG`) and integer/member encodings. `enum` values define BTF kinds from `BTF_KIND_INT` through `BTF_KIND_ENUM64`, plus variable and function linkage constants.

Control flow, state, and persistence: this header defines a serialized format. Parsers first validate `BTF_MAGIC`, `BTF_VERSION`, and section offsets in `btf_header`, then walk type records and use `kind` and `vlen` to determine which trailing records follow. Persistent state is the BTF blob embedded in ELF sections, kernel BTF, or BPF object metadata.

Dependencies and integration points: depends on `<linux/types.h>`. It integrates clang/pahole-generated BTF, kernel BPF verifier type checks, CO-RE relocations, bpftool inspection, and BPF map/program metadata.

Risks and test signals: risks include integer overflow in offset/length walking, invalid `vlen`, string table out-of-range references, enum64 sign handling, and bitfield interpretation through `kind_flag`. Tests should parse malformed BTF, verify round-trip encoding, exercise every kind, and load BPF objects that use structs, datasecs, decl/type tags, and 64-bit enums.
