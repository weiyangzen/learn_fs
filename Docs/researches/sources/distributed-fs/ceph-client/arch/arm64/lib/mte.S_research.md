# sources/distributed-fs/ceph-client/arch/arm64/lib/mte.S

Purpose: implements ARM64 Memory Tagging Extension page tag operations and ptrace tag copy helpers.

Important APIs/types/functions: `multitag_transfer_size`, `mte_clear_page_tags`, `mte_zero_clear_page_tags`, `mte_copy_page_tags`, `mte_copy_tags_from_user`, `mte_copy_tags_to_user`, `mte_save_page_tags`, and `mte_restore_page_tags`.

Control flow: page clear/copy loops use GMID-derived multi-tag block size with `stgm`/`ldgm`. Zero-clear uses DC GZVA when permitted, otherwise `stz2g` granule stores. Ptrace helpers transfer one tag byte per MTE granule between user buffers and kernel-address tags, with `USER` fixups returning the count copied. Save/restore compresses or expands page tags into `MTE_PAGE_TAG_STORAGE` groups.

State and persistence: mutates allocation tags attached to memory and, for zero-clear, page data. Saved tags are stored in caller-provided memory. No independent persistent state.

Dependencies/integration: built for `CONFIG_ARM64_MTE`; depends on ARMv8.5 memtag instructions, MTE granule constants, uaccess exception macros, page size, and ptrace/swap/page-copy MTE paths.

Risks: tag operations require correct address tag clearing and granule alignment. User tag copy residual counts must be exact. Save/restore packing assumes tag storage size and GMID block size match architecture expectations.

Test signals: MTE page allocation/tagging tests, ptrace PEEK/POKE MTE tags with partial faults, swap save/restore, huge/small page tag copy, DC GZVA availability matrix, and tag preservation across migration/COW.
