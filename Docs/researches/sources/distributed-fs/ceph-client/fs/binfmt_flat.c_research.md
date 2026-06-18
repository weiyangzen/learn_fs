# sources/distributed-fs/ceph-client/fs/binfmt_flat.c

## Purpose
Implements the Linux `bFLT`/FLAT executable loader, primarily for embedded and NOMMU systems. It supports direct ROM text mappings, fully copied RAM mappings, optional compressed FLAT images, architecture-specific relocation formats, GOT relocation, and initial userspace stack construction.

## Important APIs, Types, And Functions
The file registers `flat_format` with the exec subsystem through `register_binfmt()`. `load_flat_binary()` is the binary-format entry point; it prepares argument-stack sizing, calls `load_flat_file()`, fills shared-library data pointers, sets the active binfmt, builds argument tables, finalizes exec, and calls `start_thread()`.

`struct lib_info` tracks the loaded program/library segments: `start_code`, `start_data`, `start_brk`, `text_len`, entry address, build date, and loaded state. `create_flat_tables()` builds `argc`, optional `argvp`/`envp`, `argv[]`, and `envp[]`. Optional `CONFIG_BINFMT_ZFLAT` adds `decompress_exec()` for gzip-wrapped text/data. `calc_reloc()` translates FLAT-relative offsets into runtime addresses, while `old_reloc()`, `skip_got_header()`, `flat_get_addr_from_rp()`, and `flat_put_addr_at_rp()` handle relocation variants.

## Control Flow
`load_flat_binary()` computes extra stack space for argument strings and pointer arrays, then delegates to `load_flat_file()`. `load_flat_file()` parses the `struct flat_hdr` from `bprm->buf`, validates magic, version, field sizes, compression flags, and `RLIMIT_DATA`, then calls `begin_new_exec()`. After that point it sets `PER_LINUX_32BIT`, runs `setup_new_exec()`, calculates mapping sizes, and chooses either a split text/data mapping or one combined RAM mapping.

For NOMMU non-RAM non-gzip images, text is mapped from the executable file and data/BSS/relocation space is allocated anonymously. Otherwise, text and data are copied or decompressed into an anonymous region, with MMU builds using kernel buffers for decompression copy-back. The loader fills `mm->start_code`, `end_code`, data bounds, `start_brk`, `brk`, and NOMMU `context.end_brk`.

Relocation then proceeds in two phases. GOTPIC entries at the start of the data segment are relocated in place until a `0xffffffff` terminator, with RISC-V GOT PLT headers skipped. Explicit relocation table entries are read, translated to pointer locations, the pointer value is fetched with architecture helpers, and nonzero values are relocated back into place. Old format builds use `old_reloc()`. Finally instruction cache is flushed, BSS/brk/stack slack is zeroed, arguments are installed via `setup_arg_pages()` or `transfer_args_to_stack()`, and execution starts at the relocated entry.

## State And Persistence
The loader constructs an entirely new process image and persists state in `current->mm` ranges plus the relocated text/data memory. It mutates user memory during data loading, relocation, BSS zeroing, and stack-table construction. `lib_info` is transient per exec. The only durable state is the running process image; no filesystem metadata is written.

## Dependencies And Integration Points
It depends on the generic exec path, `linux/flat.h` on-disk format, architecture hooks from `asm/flat.h`, VFS `read_code()` and `vm_mmap()`, zlib when compressed FLAT support is enabled, RLIMIT enforcement, cache flushing, and NOMMU `mm->context.end_brk`. Kconfig options change ABI details such as old format support, compressed image support, data-start-offset handling, and whether `argvp`/`envp` are placed on stack.

## Risks
The highest-risk areas are relocation validation, user-memory access, and size arithmetic. Corrupt headers can try to overflow mapping calculations, relocation offsets can target outside text/data, and compressed images can exercise less common copy paths. The code calls `begin_new_exec()` before mapping and relocation are complete, so late failures occur after the previous program image is committed away. The relocation path also sends `SIGSEGV` on invalid offsets, so tests must distinguish loader rejection from process kill semantics.

## Test Signals
Coverage should include valid uncompressed FLAT binaries, RAM and split text/data mappings, NOMMU argument-heavy executions, GOTPIC relocation, zero-valued relocation entries, RISC-V GOT header skipping, old format images when enabled, and zflat images with full-image and data-only compression. Negative tests should cover bad magic, unsupported revisions, oversized header fields, invalid relocation offsets, insufficient data limit, truncated compressed input, and BSS/stack zeroing.
