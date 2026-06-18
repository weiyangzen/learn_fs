# sources/distributed-fs/ceph-client/drivers/video/sticore.c

Purpose: HP PARISC STI firmware core for graphics console support. It discovers STI ROMs on native PARISC and PCI graphics cards, copies and interprets ROM metadata/fonts, initializes firmware global configuration, exports font/block drawing helpers, and provides access to detected STI devices.

Important APIs, types, and functions: exported console helpers include `sti_putc`, `sti_set`, `sti_clear`, `sti_bmove`, `sti_font_convert_bytemode`, `sti_get_rom`, and `sti_call`. Discovery/setup functions include `sti_read_rom`, `sti_try_rom_generic`, `sti_init_glob_cfg`, `sti_init_graph`, `sti_inq_conf`, `sticore_pa_init`, `sticore_pci_init`, and `sti_init_roms`. Global state tracks `default_sti`, `num_sti_roms`, and `sti_roms`.

Control flow: boot options may set default STI path and font selection. `sti_get_rom` lazily initializes ROM discovery, registering PARISC and PCI drivers. Probe tries ROM addresses from device data, HPA, PAGE0, or enabled PCI ROM BAR. `sti_try_rom_generic` validates ROM signatures, handles PCI image indirection, copies byte- or word-mode ROMs, cooks font lists, maps region descriptors to physical addresses, allocates low-memory shared STI data, disables PCI ROM after copying, calls firmware `init_graph`, queries configuration, and registers the STI in global arrays. Drawing helpers build firmware inptr/outptr structures, handle 32-bit ROM calls on 64-bit kernels by using low-memory copies, serialize calls with `sti->lock`, and retry while firmware returns busy.

State and persistence: persistent runtime state is global detected ROM list, selected default STI, per-STI copied ROM/font/config data, firmware global config, and hardware/firmware initialized graphics state. Fonts and STI data are allocated with low-memory constraints. No storage persistence.

Dependencies and integration points: PARISC-specific PDC, GSC, hardware path, page0, cache flush, low-memory allocation, optional PCI and PPC-style font support. It integrates with sticon/console users through `<video/sticore.h>` exports and with PARISC/PCI device buses.

Risks: architecture- and firmware-specific code with real-mode STI calls; pointer width handling is critical and guarded by overflow warnings. `sticore_pci_remove` is a `BUG()`, so removal is not supported. Some older GSC/STI card revisions are explicitly rejected. ROM copying and byte-mode conversion depend on exact firmware layout. Global lazy init and fixed `MAX_STI_ROMS` limit scalability.

Test signals: PARISC boot on native and PCI STI hardware; boot parameters `sti=` and `sti_font=` with built-in and ROM fonts; 32-bit and 64-bit kernels with 32-bit and 64-bit STI ROMs; console putc/clear/bmove rendering; unsupported card revision rejection; PCI ROM enable/disable behavior; suspend/removal expectations documented as unsupported.
