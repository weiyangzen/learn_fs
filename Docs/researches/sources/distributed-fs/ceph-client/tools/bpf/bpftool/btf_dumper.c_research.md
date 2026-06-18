<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf_dumper.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf_dumper.c

Purpose: this file formats typed BTF data values and BTF line-info snippets for bpftool map/program output. It bridges raw bytes plus BTF metadata into JSON/plain textual representations.

Important APIs/functions: `btf_dumper_type()` dispatches recursive value dumping through `btf_dumper_do_type()`. Helpers handle pointers (`btf_dumper_ptr()`), modifiers, enums and enum64, arrays including char arrays as strings, 128-bit integers, bitfields, ints, structs/unions, vars, and datasecs. `btf_dumper_type_only()` renders type-only/function signatures. `btf_dump_linfo_plain()`, `btf_dump_linfo_json()`, and `btf_dump_linfo_dotlabel()` print source line info for plain, JSON, and graph labels.

Control flow: value dumping resolves BTF kind and recursively advances byte offsets based on resolved element sizes and bit offsets. Struct/union dumping iterates members, handling kflag bitfield encodings. Function pointer dumping can optionally interpret a 32-bit pointer value as a BPF program ID and print the matching program function name plus ID. Type-only rendering recursively prints C-like signatures for int, typedef, float, struct, union, enum, array, pointer, modifiers, function prototypes, functions, vars, and datasecs.

State and persistence: the dumper itself is stateless apart from the caller-provided `struct btf_dumper`, JSON writer, and flags such as `is_plain_text` and `prog_id_as_func_ptr`. It opens program FDs transiently when resolving program IDs in function pointer fields, then closes them.

Dependencies and integration points: it depends on libbpf BTF APIs, bpftool JSON writer, BPF program info syscalls, and the `struct btf_dumper` contract from `main.h`. `cfg.c` and xlated dumpers use line-info dot labels for graph output.

Risks: many routines trust that caller-provided data buffers are large enough for the BTF type; size enforcement belongs to callers. Pointer dumping casts to `unsigned long`, so output follows host pointer width. Char array detection rejects non-printable strings and requires a terminator within array length. Bitfield and 128-bit handling is endian-sensitive through `__BIG_ENDIAN_BITFIELD`/`__LITTLE_ENDIAN_BITFIELD`. Unsupported or forward kinds produce marker strings and often `-EINVAL`, which can leave partially emitted JSON objects.

Test signals: typed map dump tests should cover ints of all widths/encodings, bool, char printable/nonprintable, enum/enum64 named and unknown values, arrays, strings, nested structs/unions, bitfields crossing bytes, 128-bit values, datasecs, vars, pointers with and without program-ID resolution, and plain/json/dot line-info escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf_dumper.c -->
