# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-aux.h

Purpose: Declares perf's DWARF auxiliary API exported by `dwarf-aux.c`. It exposes CU, DIE, type, variable, line, scope, CFA, and member/pointer helpers to probe and annotation code.

Important APIs and types: Includes elfutils `Dwarf`, `Dwarf_Die`, and `Dwarf_Addr` types. Defines the `DIE_FIND_CB_*` callback protocol, `line_walk_callback_t`, and `struct die_var_type`, which records type DIE offset, address/range, register, offset, and whether a register stores the variable address. Public functions cover source/line lookup, function and inline search, type resolution, name matching, variable and member lookup, variable collection, prologue skipping, scope discovery, CFA decoding, and pointer/member type resolution.

Control flow and state: The header has no executable flow, but it establishes ownership contracts: callers provide DIE buffers and `strbuf`s, receive borrowed libdw strings, and must free linked lists from variable collection. The callback enum controls recursive traversal behavior used by `die_find_child`.

Dependencies and integration: Pulls in `<dwarf.h>`, elfutils libdw/libdwfl, and elfutils version headers. Forward-declares `struct strbuf` to avoid pulling in perf's string buffer implementation. It is a central contract between DWARF consumers in perf and the libdw implementation.

Risks: ABI/API risk is mostly semantic: many functions return negative errno values or NULL depending on operation, so callers must distinguish absent debug info from unsupported expressions. `struct die_var_type` stores DIE offsets rather than references, requiring consumers to resolve them against the same DWARF object.

Test signals: Header-level test signals come from successful builds with and without libdw users and from compile coverage of callers that exercise all prototypes, especially variable-location and member-type APIs.
