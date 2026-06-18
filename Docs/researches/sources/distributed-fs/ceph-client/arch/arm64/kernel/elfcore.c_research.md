## sources/distributed-fs/ceph-client/arch/arm64/kernel/elfcore.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/elfcore.c` adds ARM64 Memory Tagging Extension
metadata to ELF core dumps. When MTE is supported, it emits extra program headers and tag storage
for VMAs marked `VM_MTE`.

### Important APIs, Types, And Functions
`for_each_mte_vma` iterates coredump VMA metadata only when `system_supports_mte()` is true and the
VMA has `VM_MTE`. `mte_vma_tag_dump_size()` calculates compact tag storage size. `mte_dump_tag_range()`
saves tags page by page. Generic ELF hooks are `elf_core_extra_phdrs()`,
`elf_core_write_extra_phdrs()`, `elf_core_extra_data_size()`, and `elf_core_write_extra_data()`.

### Control Flow
The core dump code first asks for the number and size of extra headers/data. For each MTE VMA,
`elf_core_write_extra_phdrs()` emits a `PT_AARCH64_MEMTAG_MTE` program header whose file size is
the compact tag dump and whose memory size is the VMA range. Data emission then walks pages in
`mte_dump_tag_range()`: missing zero pages and untagged pages are represented by skipped zero tag
storage, tagged pages allocate temporary storage, save page tags, and emit them to the dump.

### State, Persistence, And Dependencies
The file has no long-lived state. It reads core VMA metadata, page table dump pages, page MTE tag
state, and MTE tag storage. Its persistence is the generated core file contents. Dependencies are
generic coredump/ELF helpers, `get_dump_page()`, `dump_emit()`, `dump_skip()`, page reference
management, and ARM64 MTE helpers.

### Integration Points
ELF core dump generation calls these architecture hooks. Debuggers and postmortem tools consume the
`PT_AARCH64_MEMTAG_MTE` segments to reconstruct allocation tags. This is relevant to diagnosing
memory corruption in kernel-provided user processes and filesystem clients running on MTE-enabled
systems.

### Risks
Tag data must stay aligned with dumped pages; skipping zero or untagged pages must produce exactly
the expected zero-length representation. Allocation failure aborts extra data emission. Incorrect
page reference handling can leak pages. The code assumes start/end/dump sizes are page-aligned by
the core dump layer.

### Test Signals
User MTE coredump tests, comparison of tag segments with live process tags, sparse mapping core
dumps, PROT_EXEC-only mappings, untagged pages in MTE VMAs, allocation failure injection, and
debugger parsing of `PT_AARCH64_MEMTAG_MTE` segments validate behavior.
