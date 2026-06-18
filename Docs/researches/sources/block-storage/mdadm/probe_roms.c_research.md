# File Research: sources/block-storage/mdadm/probe_roms.c

Purpose: scans legacy x86 option ROM space, mainly the adapter ROM window from `0xc0000` to `0xf0000`, and exposes discovered adapter ROM ranges to a callback.

Key behavior:
- `probe_roms_init(align)` validates `align` as `512` or `2048`, initializes adapter ROM resource storage, installs a `SIGBUS` handler, opens `/dev/mem`, and `mmap`s the option ROM physical range.
- `probe_roms_exit()` restores `SIGBUS`, closes `/dev/mem`, unmaps memory, and frees adapter ROM resource nodes.
- `probe_roms()` scans video ROM, extension ROM, and adapter ROM regions. It checks `0xaa55` signatures, length byte at offset `2`, checksum validity, and PCI data pointer at offset `0x18`.
- `scan_adapter_roms(scan_fn fn)` iterates discovered adapter ROM resources and passes virtual start/end/data pointers to the callback.

Important implementation details:
- Reads are wrapped in `probe_address8()` and `probe_address16()` so a `SIGBUS` during `/dev/mem` access marks the probe failed rather than crashing immediately.
- The scanner trusts the length byte only if checksum passes and the range fits before the upper bound.
- Adapter ROM resource list starts with one preallocated node and allocates more only when additional ROMs are found.
- `isa_bus_to_virt()` maps physical ISA addresses into the single mmap region.

Dependencies:
- Includes `probe_roms.h`, `mdadm.h`, Linux endian/types helpers, `/dev/mem`, `mmap`, and signal wrapper `signal_s`.
- Intended consumers are mdadm code paths that need to inspect BIOS/option-ROM metadata.

Risks and notes:
- Requires privileged `/dev/mem` access and is platform-specific to legacy x86 ROM layout.
- Pointer arithmetic is done on `void *` in `isa_bus_to_virt`, relying on compiler extension behavior.
- `roms_deinit()` frees `adapter_rom_resources` but does not reset the pointer to `NULL`; repeated init/exit cycles depend on normal call ordering.
