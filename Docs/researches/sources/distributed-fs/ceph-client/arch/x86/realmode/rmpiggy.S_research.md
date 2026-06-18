<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rmpiggy.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rmpiggy.S

## Purpose
`rmpiggy.S` embeds the generated real-mode binary and relocation stream into kernel init data so `init.c` can copy them to low memory.

## Important APIs, types, and functions
It exports `real_mode_blob`, `real_mode_blob_end`, and `real_mode_relocs` using `.incbin` of `realmode.bin` and `realmode.relocs`.

## Control flow
During vmlinux link the generated files become aligned `.init.data`. Early init copies the blob and walks the relocation data.

## State and persistence behavior
State is build-time binary data only; it is freed with init data after boot once copied and initialized.

## Dependencies and integration points
It depends on `rm/Makefile` producing the two included files before assembly and on `PAGE_SIZE` alignment.

## Risks and edge cases
Missing or stale included binaries produce broken trampoline setup. Alignment matters for later page permission management.

## Test signals
Signals are successful vmlinux link, correct blob size in `init.c`, and real-mode relocation processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rmpiggy.S -->
