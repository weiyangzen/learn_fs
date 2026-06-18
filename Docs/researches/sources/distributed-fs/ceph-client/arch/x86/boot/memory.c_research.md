# sources/distributed-fs/ceph-client/arch/x86/boot/memory.c

Purpose: detects system memory through BIOS interfaces and stores results in boot parameters.

Important APIs and state: exports `detect_memory()`. Helpers query INT 15h E820, E801, and AH=88h. State is written to `boot_params.e820_table`, `e820_entries`, `alt_mem_k`, and `screen_info.ext_mem_k`.

Control flow: E820 loops with a static zeroed buffer to handle BIOSes that partially update entries, copies valid SMAP entries until continuation ends or table fills, and zeroes count on signature loss. E801 and 88h provide older fallback size fields.

Dependencies and integration: called by `main()` before protected mode. Later kernel memory initialization uses these boot protocol fields.

Risks and test signals: firmware bugs can produce partial or bogus maps; E820 signature loss intentionally invalidates the map. Test with QEMU e820 variants, table-full conditions, non-SMAP failure, and legacy memory-size fallback behavior.
