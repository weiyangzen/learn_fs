## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_mm.c

Purpose: AST VRAM sizing and write-combined BAR0 mapping.

Important functions are `ast_get_vram_size` and `ast_mm_init`. VRAM size is decoded from indexed register `0xaa` and reduced by reserved-memory bits in register `0x99`.

Control flow: `ast_mm_init` gets BAR0 base/length, reserves/adds write-combining memtype best-effort, computes usable VRAM, maps that range with `devm_ioremap_wc`, and records `ast->vram`, `vram_base`, and `vram_size`. It does not create a full GEM memory manager; scanout uses shmem shadow copies into this mapped VRAM.

State persists in `ast_device` VRAM fields and architecture WC reservations. Dependencies are PCI BAR resources, DRM managed lifetime, AST indexed register access, and cursor/primary plane sizing. Risks include no explicit check that decoded VRAM size is <= BAR0 length, unknown default initialization if register values fall outside documented cases, reserved DP501 memory shrinking primary framebuffer space, and performance fallback if WC reservation fails. Test signals are successful probe mapping, correct framebuffer max mode validation, cursor offset calculation, and no BAR overrun on boards with reserved memory.
