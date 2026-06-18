# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_debugfs.c

Purpose: registers device-level debugfs diagnostics for the Loongson DRM driver.

Important APIs/types/functions: debugfs show functions for chip identity, DRM MM, GFX PLL clocks, benchmark, PCI command enabling, and `lsdc_debugfs_init`.

Control flow: `lsdc_debugfs_init` stores `ldev` in every info entry, creates files under DRM debugfs root, and delegates TTM debugfs setup. Individual show callbacks print CPU PRID/model, VMA offset manager, GFX PLL rates, benchmark results, BO list, or PCI command changes.

State and persistence: mostly read-only diagnostic state. `dc_enable` mutates PCI command bits to enable IO/MEM, so it has side effects.

Dependencies and integration points: depends on `lsdc_probe.c` CPU PRID helper, `lsdc_gfxpll`, benchmark, GEM BO reporting, TTM debugfs, PCI config access, and DRM debugfs.

Risks and test signals: debugfs callbacks can be invoked while device state changes; BO list paths use internal locking in callees. Test file creation, read stability under modesets, benchmark cleanup, and `dc_enable` on systems where firmware left PCI bits disabled.
