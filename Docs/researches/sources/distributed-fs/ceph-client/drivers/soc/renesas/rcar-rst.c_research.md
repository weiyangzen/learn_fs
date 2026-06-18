# sources/distributed-fs/ceph-client/drivers/soc/renesas/rcar-rst.c

## Purpose

`rcar-rst.c` initializes Renesas R-Car/RZ reset controller support. It reads and caches mode pins, enables watchdog-reset behavior on selected generations, and exports a helper for programming Gen3 realtime-core boot addresses.

## Important APIs, Types, and Functions

`struct rst_config` defines mode register offset plus optional `configure` and `set_rproc_boot_addr` callbacks. `rcar_rst_init()` finds a matching reset node, maps registers, stores `saved_mode`, and runs configuration. Public APIs are `rcar_rst_read_mode_pins()` and exported `rcar_rst_set_rproc_boot_addr()`. Gen-specific helpers write WDTRSTCR variants and CR7BAR.

## Control Flow

The first call to `rcar_rst_read_mode_pins()` lazily calls `rcar_rst_init()` if needed. Init matches DT compatible, maps MMIO, stores global base and boot-address callback, reads mode pins, and enables watchdog reset where required. Remoteproc boot-address calls validate 256 KiB alignment through `CR7BAR_MASK`, then write CR7BAR and enable it.

## State and Persistence Behavior

Global `rcar_rst_base`, `saved_mode`, and function pointer persist after init. `saved_mode` is `__initdata`, but the public read path uses it after init-time setup in normal early-call patterns. Hardware writes persist in reset-controller registers.

## Dependencies and Integration Points

It depends on OF address mapping, Renesas reset DT compatibles, and `linux/soc/renesas/rcar-rst.h`. Consumers include SoC setup and remoteproc code needing mode pins or CR7 boot address programming.

## Risks and Edge Cases

Global singleton design assumes one reset controller. Failure after mapping does not unmap because this is init-time infrastructure. Boot address validation rejects any low bits outside `CR7BAR_MASK`; callers must pass aligned physical addresses. New Gen4/Gen5 variants require correct modemr and watchdog behavior.

## Test Signals

Boot supported Gen1/2/3/4 and RZ/G variants, verify mode-pin values, watchdog reset enable writes, remoteproc boot address alignment rejection/acceptance, and behavior when no matching node exists.
