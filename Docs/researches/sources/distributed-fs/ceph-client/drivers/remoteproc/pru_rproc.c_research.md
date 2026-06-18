# sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.c

## Purpose

`pru_rproc.c` is the TI PRU-ICSS/ICSSG remoteproc driver for PRU, RTU, and Tx_PRU cores. It exposes PRU cores as remoteproc instances, maps PRU instruction/control/debug regions, provides client ownership APIs, configures PRUSS GP mux and constant tables, parses PRU-specific firmware sections, sets up PRUSS interrupt mappings, implements PRU-specific firmware loading quirks, and provides debugfs register/single-step controls.

## Important APIs, types, and functions

- `struct pru_rproc` stores PRU id, parent PRUSS pointer, rproc pointer, memory regions, owning client node, firmware name, interrupt map data, register RMW lock, debug single-step state, event mappings, and saved GPMUX value.
- Exported APIs are `pru_rproc_get()`, `pru_rproc_put()`, and `pru_rproc_set_ctable()`.
- `pru_control_*()` helpers read/write/update control registers under spinlock for RMW operations.
- `pru_rproc_get()` enforces single-client ownership through `client_np`, sets sysfs read-only while a kernel client owns the PRU, saves/restores GPMUX, optionally applies `ti,pruss-gp-mux-sel`, and optionally selects per-client firmware.
- `pru_handle_intrmap()` consumes `.pru_irq_map` data and creates IRQ mappings in the sibling PRUSS interrupt controller.
- `pru_rproc_start()` configures interrupt mappings and writes the start PC plus enable bit to `PRU_CTRL_CTRL`; `pru_rproc_stop()` clears enable and disposes mappings.
- `pru_d_da_to_va()` and `pru_i_da_to_va()` translate data and instruction address spaces. `pru_rproc_da_to_va()` exposes only data RAMs to remoteproc clients.
- `pru_rproc_load_elf_segments()` handles PRU program/data segment copying and K3 4-byte copy restrictions.
- `pru_rproc_parse_fw()` loads optional resource tables and finds `.pru_irq_map`.
- Debugfs `regs` and `single_step` expose control/debug registers and single-step execution.

## Control flow

Probe matches PRU/RTU/Tx_PRU data, parses firmware name, allocates a remoteproc, overrides `.load` and `.parse_fw`, disables recovery and auto-boot, stores PRUSS parent state, maps `iram`, `control`, and `debug` resources, derives PRU id from IRAM physical offset, registers remoteproc, and creates debugfs entries.

Kernel clients call `pru_rproc_get()` through their DT `ti,prus` phandle. The function validates that the phandle is a PRU rproc, ensures exclusive ownership, saves and optionally changes GPMUX, optionally changes firmware, and returns the rproc. `pru_rproc_put()` restores GPMUX and firmware, clears ownership, re-enables sysfs writes, and drops the rproc reference.

Firmware parse loads a standard resource table if present and locates `.pru_irq_map` without loading it into PRU memory. Start validates and maps the interrupt map into the PRUSS INTC, then writes enable and boot PC. Firmware load distinguishes executable PT_LOAD segments as IRAM and others as data RAM. K3 cores use a custom 4-byte copy routine because unaligned/8-byte writes to IRAM corrupt or fault.

## State and persistence behavior

Ownership state persists in `client_np` and `rproc->sysfs_read_only` while a client holds the PRU. GPMUX and selected firmware are saved/restored around that ownership. Interrupt mappings are firmware-specific and exist only while the rproc is running. Debug single-step state stores the previous continuous control register value for restoration. Hardware state persists in PRU control registers, constant table registers, PRUSS INTC mappings, local IRAM, data RAMs, and GPMUX configuration.

## Dependencies and integration points

The driver depends on the PRUSS core driver, PRUSS memory regions, PRUSS config helpers, IRQ domains, OF phandles, remoteproc ELF helpers, debugfs, and public PRUSS/PRU headers. DT must provide memory resources named `iram`, `control`, and `debug`, firmware names, compatible strings for SoC/core type, and optional client properties `ti,prus`, `ti,pruss-gp-mux-sel`, and per-index `firmware-name`.

## Risks and edge cases

- PRU has separate instruction and data address spaces with overlapping local addresses. Generic clients get only data-space translation; loader code must correctly classify executable segments.
- K3 firmware load rejects unaligned destination or size in `pru_rproc_memcpy()`, so firmware linkers must align IRAM segments to 4 bytes.
- `.pru_irq_map` points into the firmware buffer and is cleared after start; delayed use after `rproc_start()` would be invalid.
- `pru_d_da_to_va()` does not explicitly check `da >= PRU_PDRAM_DA` for primary DRAM because that base is zero; this is fine today but depends on constants.
- Debug register reads are blocked while running, but single-step writes can change control state and should remain a debug-only facility.
- Client ownership changes sysfs mutability and firmware selection; error paths must always call `pru_rproc_put()` to restore GPMUX and references.

## Test signals

Build all PRU/RTU/Tx_PRU compatibles. Tests should cover client get/put exclusivity, GPMUX save/restore, per-client firmware selection, constant table programming, debugfs `regs` and `single_step`, ELF data/IRAM loading, K3 aligned-copy failures, `.resource_table` optional handling, `.pru_irq_map` validation and IRQ mapping cleanup, PRU0/PRU1 DRAM swap behavior, shared RAM translation, and start/stop register values.
