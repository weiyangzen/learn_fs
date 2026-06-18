# sources/distributed-fs/ceph-client/scripts/faddr2line

Purpose: Resolves kernel stack dump `function+offset[/size]` entries to source lines, handling KASLR-style function-relative addresses and inline call chains better than direct `addr2line`.

Important APIs/functions: `run_readelf()` captures ELF header, section headers, and symbols. `check_vmlinux()` detects EXEC/DYN vmlinux. `init_addr2line()` starts a persistent `addr2line` coprocess for vmlinux. `run_addr2line()` queries either the coprocess or one-shot section-specific addr2line. `find_dir_prefix()` strips source-tree prefixes using `start_kernel`. `__faddr2line()` matches symbols, computes kallsyms-like symbol sizes, validates offsets/user sizes, and prints source or `--list` context.

Control flow: Parses optional `--list`, validates tools and debug info, reads ELF metadata, initializes addr2line, then processes each func+offset argument. For duplicate symbol names it prints all size-compatible matches. If no match prints warnings on a second pass.

State/persistence: Uses many shell globals (`ELF_*`, `ADDR2LINE_OUT`, `IS_VMLINUX`, `DIR_PREFIX`, `DONE`, `FIRST`). A coprocess remains active during script execution for vmlinux.

Dependencies/integration: Bash, readelf/addr2line from CROSS_COMPILE or LLVM selection, awk, grep, sed, sort, mktemp, and source files for `--list`. Used for kernel debugging.

Risks: Parses readelf text and symbol fields positionally. `--list` evaluates source paths from debug info and can fail if files are absent. Long-running coprocess handling relies on sentinel output variants from GNU/LLVM addr2line. Symbol size approximation depends on sorted section symbols and skips mapping symbols heuristically.

Test signals: vmlinux and module/object inputs, GNU and LLVM tools, duplicate symbol names with and without size, inlined functions, absent debug info, `--list`, KASLR-like function offsets, and invalid argument formats.
