# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.c

Purpose: maps and reports the Loongson shared GFX PLL used by DC, GMC, and GPU.

Important APIs/types/functions: bitfield/union representation of the 64-bit PLL register, `loongson_gfxpll_get_rates`, `loongson_gfxpll_print`, `loongson_gfxpll_init/fini`, and `loongson_gfxpll_create`.

Control flow: create allocates the PLL object, derives register base from chip descriptor, assigns funcs, maps MMIO, initializes reference clock, prints rates, stores the object in caller output, and registers managed cleanup. Rate reading snapshots the register, updates cached parameters, computes pre-output and per-consumer MHz values. Update is currently a TODO no-op.

State and persistence: object stores MMIO pointer, register base/size, funcs, and cached parameters. Hardware PLL settings are read but not modified by the current update function.

Dependencies and integration points: used by core device creation and debugfs clock reporting. Depends on chip descriptor config base/offsets and DRM managed cleanup.

Risks and test signals: division by zero is possible if firmware left dividers zero. No-op update means clock changes are unsupported here. Test debugfs clock output on both chips, 32-bit versus 64-bit register access, and cleanup after probe failure.
