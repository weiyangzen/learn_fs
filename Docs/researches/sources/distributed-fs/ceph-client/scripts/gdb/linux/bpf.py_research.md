# sources/distributed-fs/ceph-client/scripts/gdb/linux/bpf.py

Purpose: Provides GDB-side helpers for BPF kernel debugging, including tracking BPF ksyms/programs and generating temporary debug objects for JITed BPF code.

Important APIs/classes: `list_ksyms()`, `list_progs()`, `get_ksym_name()`, `KsymMonitor`, `ProgMonitor`, breakpoint classes for add/remove events, `btf_str_by_offset()`, `LInfoIter`, and `generate_debug_obj()`.

Control flow: Feature availability is gated by generated constants for BPF, BPF JIT, and BPF syscall support. Monitors set internal breakpoints on BPF add/remove functions and notify callbacks for initial and dynamic objects. `generate_debug_obj()` reads JITed code bytes, writes a temporary assembly file with `.byte` directives and `.loc` records from BPF line info, invokes `as`, and returns a temporary object file.

State/persistence: Monitors hold breakpoints until `delete()`. Temporary `.s` and `.o` files are created; returned object remains open via `NamedTemporaryFile`. GDB cached types are module globals.

Dependencies/integration: GDB Python API, generated `linux.constants`, Linux helper modules `lists`, `radixtree`, `utils`, BPF kernel data structures, BTF line info, JSON escaping, tempfile, subprocess, and host assembler `as`.

Risks: Kernel struct layout changes can break field access. Missing assembler returns `None`. Temporary debug object lifetime is tied to the returned file object. Breakpoint symbols must exist and match expected argument names.

Test signals: Kernels with/without BPF JIT/syscall, existing and newly loaded BPF programs, subprogram enumeration, BTF line-info mapping, missing `as`, and breakpoint cleanup.
