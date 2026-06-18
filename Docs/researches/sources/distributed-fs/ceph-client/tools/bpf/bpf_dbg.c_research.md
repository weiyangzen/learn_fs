<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_dbg.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_dbg.c

Purpose: this is an interactive classic BPF debugger and interpreter. It loads classic BPF bytecode, validates it with the kernel, maps a tcpdump-format pcap file, and lets users run, step, disassemble, dump, select packets, and set breakpoints.

Important APIs/types/functions: core types include `struct shell_cmd`, `struct pcap_filehdr`, `struct pcap_pkthdr`, and `struct bpf_regs`. Global state includes `bpf_image`, `bpf_prog_len`, `bpf_breakpoints`, register history `bpf_regs`, current registers `bpf_curr`, pcap file descriptor/mapping/cursor, and packet counter. Execution is handled by `bpf_single_step()`, `bpf_run_all()`, and `bpf_run_stepping()`. Loading is handled by `cmd_load_bpf()`, `try_load_pcap()`, and `cmd_load()`. Shell commands are dispatched through `execf()` and readline completion.

Control flow: `main()` optionally opens command input/output files and enters `run_shell_loop()`. The shell parses full command names from `cmds`. `load bpf` parses the comma-separated `len,code jt jf k,...` format and validates the program with `SO_ATTACH_FILTER`. `load pcap` mmaps a regular pcap file and validates magic. `run` executes the current program over packets until the end, a requested limit, or a breakpoint. `step` advances a configurable number of instructions, supports negative register-history restore, and moves to the next packet after return. `select` positions the pcap cursor by packet index.

State and persistence: process state persists across shell commands: loaded program, mapped pcap, packet cursor, breakpoints, current registers, and register history. Readline history is read from and written to `$HOME/.bpf_dbg_history`; readline init may come from `$HOME/.bpf_dbg_init`. No pcap or BPF program is modified.

Dependencies and integration points: it depends on readline/history, mmap, pcap classic file format, Linux classic BPF socket filter validation, and classic BPF instruction constants. It intentionally does not support kernel BPF extensions during interpretation after validation detects `SKF_AD_OFF` loads.

Risks: pcap parsing assumes native tcpdump magic endianness only and does not support swapped magic or pcapng. It uses `MAP_LOCKED`, which can fail under low memlock limits. Some bounds checks use `>= pcap_map_size`, making exact-end packets invalid. `BPF_LDX_W | BPF_LEN` appears to set `A` rather than `X`, which is a possible interpreter bug. Long-running BPF programs rely on kernel validation but the local interpreter does not independently enforce every safety property. `getenv("HOME")` can be NULL, which would break history path construction.

Test signals: tests should load known `bpf_asm` and `tcpdump -ddd` programs, run against small pcaps with pass/fail expectations, verify stepping/backtracking, breakpoint dumps, disassembly formatting, pcap cursor wrapping, malformed pcap rejection, oversized/short BPF strings, and interpreter agreement with kernel/socket filter behavior for representative instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_dbg.c -->
