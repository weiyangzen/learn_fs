# sources/distributed-fs/ceph-client/scripts/gdb/linux/symbols.py

## Purpose
`symbols.py` registers `lx-symbols`, a symbol loader that reloads vmlinux, loaded module symbols, and optional JITed BPF debug objects.

## Important APIs, Types, and Functions
`LxSymbols` tracks module paths, module files, loaded modules, load breakpoints, BPF monitors, BPF program maps, and temporary debug objects. It implements module file scanning, module section argument construction, `load_module_symbols()`, `load_all_symbols()`, BPF add/remove handlers, and cleanup. s390 helpers handle vmcore KASLR offsets and decompressor state.

## Control Flow
`invoke()` optionally skips s390 decompressor execution, parses paths and `-bpf`, clears previous monitors, reloads vmlinux, loads all module symbols, restores breakpoint enabled state, and installs a module-load breakpoint. With `-bpf`, it creates BPF monitors that add or remove symbol files as BPF ksyms appear.

## State and Persistence Behavior
The command mutates the GDB session state: symbol files are dropped and reloaded, breakpoints are temporarily disabled by GDB and restored, internal loaded-module/BPF dictionaries persist, and temporary BPF debug objects remain until cleanup.

## Dependencies and Integration Points
It integrates with `modules.py`, `bpf.py`, `utils.pagination_off()`, and GDB breakpoint/objfile APIs. It depends on local `.ko`/`.ko.debug` files and kernel module section metadata.

## Risks and Test Signals
Wrong module search paths produce missing symbols; section layout mismatches produce misleading addresses. BPF object cleanup is important to avoid stale temp files. Test module load/unload refresh, s390 vmcore offsets, breakpoint preservation, and BPF JIT symbol add/remove.
