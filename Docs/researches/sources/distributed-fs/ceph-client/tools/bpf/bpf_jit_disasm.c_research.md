<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_jit_disasm.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_jit_disasm.c

Purpose: this tool extracts the last BPF JIT image dumped in kernel logs or a supplied log file and disassembles it with binutils, or writes the raw image to a file.

Important APIs/functions: `get_klog_buff()` uses `klogctl()` to read kernel log contents. `get_flog_buff()` reads a regular file. `get_last_jit_image()` searches for the last `flen=... proglen=... pass=... image=...` header and parses following `JIT code` hex lines into a byte buffer. `get_asm_insns()` initializes BFD/disassembler state using the current executable's architecture and prints disassembled instructions plus optional opcode bytes. `main()` handles `-o`, `-O`, and `-f`.

Control flow: after option parsing and `bfd_init()`, the tool reads the selected log buffer, extracts the last image, and either disassembles it to stdout or writes it to `-O` output. Extraction compiles a regex, walks to the last matching header, bounds `proglen` at 1,000,000, allocates the image, tokenizes following log lines by newline, and converts hex bytes from lines containing `JIT code`.

State and persistence: it reads kernel log or a file, allocates an image buffer, and optionally writes a binary output file with `O_CREAT|O_TRUNC`. It does not clear kernel logs or otherwise mutate kernel state.

Dependencies and integration points: it depends on BFD/opcodes, disassembler compatibility glue, `sys/klog.h`, regex, and kernel BPF JIT debug log format produced when `/proc/sys/net/core/bpf_jit_enable` is set to `2`. It is built with feature-detected disassembler ABI defines from the Makefile.

Risks: many internal failures use `assert()`, which can abort instead of returning diagnostics. The parser assumes a specific log format and mutates the log buffer with `strtok()`. It asserts that parsed bytes equal `proglen`; truncated logs abort. BFD architecture selection from the current executable may not match offloaded or cross-architecture dumps. `-h` is documented but not present in the getopt string, so it falls into usage through the default case.

Test signals: tests should use fixture log files with one and multiple JIT images, truncated images, oversized `proglen`, malformed headers, opcode display, raw output writes, stdin/file inputs, and binutils ABI variants. Integration tests require enabling BPF JIT debug logs on a test kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_jit_disasm.c -->
