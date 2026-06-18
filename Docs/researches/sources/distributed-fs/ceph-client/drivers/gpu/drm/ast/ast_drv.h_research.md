## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_drv.h

Purpose: main private header for the AST DRM driver. It defines chip/config/TX enums, device state, plane/cursor/connector/CRTC private structs, register access helpers, display mode constants, DP501/ASTDP constants, and cross-file prototypes.

Important types are `enum ast_chip`, `enum ast_tx_chip`, `enum ast_config_mode`, `enum ast_dram_layout`, `struct ast_device_quirks`, `struct ast_device`, `struct ast_plane`, `struct ast_cursor_plane`, `struct ast_connector`, and `struct ast_crtc_state`. Important helpers include generation tests, raw/indexed MMIO accessors, and `ast_read32`/`ast_write32`.

Control flow is via inline accessors and declarations consumed by all AST files. State described here includes VRAM mappings, IO register mappings, mode lock, primary/cursor planes, CRTC, per-output encoder/connector union, widescreen capability flags, TX chip, DCLK table, and DP501 firmware buffers.

Dependencies are DRM core types, Linux I/O primitives, `ast_reg.h`, and all implementation files. Risks include many raw register helpers with no locking by default, union output storage assuming one active TX path, generation enum encoding coupled to `__AST_CHIP_GEN`, and broad shared state making ordering bugs possible during probe/PM. Test signals are compile coverage, lockdep around `modeset_lock`, correct chip generation classification, and all output paths resolving their prototypes.
