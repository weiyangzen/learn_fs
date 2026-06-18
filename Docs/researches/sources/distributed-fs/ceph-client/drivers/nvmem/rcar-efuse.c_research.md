# sources/distributed-fs/ceph-client/drivers/nvmem/rcar-efuse.c

Purpose: Renesas R-Car E-FUSE/OTP read-only NVMEM provider with SoC-specific accessible windows.

Important APIs/types/functions: `struct rcar_fuse_data` selects resource bank and valid `[start,end)` window. `rcar_fuse_reg_read()` runtime-resumes the device, copies 32-bit words, and runtime-suspends. Probe constructs two keepout regions around the valid window.

Control flow: probe enables runtime PM, allocates state, maps the selected memory resource bank, computes keepouts from match data and resource size, and registers root-only OTP NVMEM. Reads are 4-byte stride copies under runtime PM.

State/persistence: fuse contents persist in hardware; driver state holds keepout table, base, and device pointer.

Dependencies/integration: compatibles for R-Car V3U, S4, V4H, and V4M variants; depends on runtime PM, NVMEM keepouts, and MMIO.

Risks: match data is assumed present. Keepout correctness is critical because the mapped resource may contain non-fuse registers around the valid region. Runtime PM errors propagate to reads.

Test signals: per-compatible bank/window selection, keepout enforcement, runtime PM failure path, and root-only read permissions.
