# sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.h

`netlink_dumper.h` is a macro formatting layer shared by `net.c` and `netlink_dumper.c`. It hides the repeated branch between JSON output through `json_wtr` and plain text output through `fprintf(stdout, ...)`.

The macros cover object and nested-object delimiters (`NET_START_OBJECT`, `NET_START_OBJECT_NESTED`, `NET_START_OBJECT_NESTED2`, `NET_END_OBJECT*`), array delimiters (`NET_START_ARRAY`, `NET_END_ARRAY`), and scalar emitters for named or bare unsigned integers and strings (`NET_DUMP_UINT`, `NET_DUMP_UINT_ONLY`, `NET_DUMP_STR`, `NET_DUMP_STR_ONLY`). Each macro references the global `json_output` flag and global `json_wtr` declared in `main.h`.

State and persistence are absent; macro expansion writes immediately to the active output stream. The header is an integration point that keeps net-related plain and JSON structures close enough that the implementation can call one macro in each logical output position. Dependencies are implicit: including files must already have access to `json_output`, `json_wtr`, `json_writer` functions, and `stdout`.

Risks are typical of multi-statement macros: no `do { } while (0)` wrapper, possible surprising control-flow interactions if used under unbraced `if` statements, no type checking for format/value pairs beyond compiler printf checks on `fprintf`, and tight coupling of plain punctuation to call-site order. Test signals should focus on net command output shape, especially nested arrays/objects, empty arrays, plain newline placement, and compiling with warnings around macro call sites.
