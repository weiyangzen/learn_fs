# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_scan.c

Purpose: general-purpose scanner for full AFS volume dumps. It can print dump headers, volume headers, vnode records, ACLs, directories, paths, debug details, and optionally generate a repaired dump.

Important APIs/functions: `parse_printflags` maps `-P` letters to `DSPRINT_*`; `parse_repairflags` maps `-R` letters to `DSFIX_*`. `setup_repair` opens `repair_output` and wires repair callbacks from `repair.c`. `print_vnode_path` calls `Path_Build` during vnode callbacks. `main` opens input with `xfopen`, enforces seekability for repair and path printing, optionally pre-scans paths with `Path_PreScan`, then calls `ParseDumpFile`.

State/persistence: normal mode reads only and prints to stdout/stderr. Repair mode writes a new dump to `-g` and appends `DumpDumpEnd` after successful parsing. Dependencies include parser library, path hash logic, repair callbacks, xfiles streams, and OpenAFS error tables.

Risks/test signals: return status is always zero at the final `exit(0)`, so automation must parse diagnostics. Path printing requires a seekable dump because it pre-scans and then rewinds. Repair output quality depends on parser recovery flags and generated defaults from `repair.c`.
