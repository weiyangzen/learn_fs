# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.h

Purpose: `clk-pllfh.h` defines the data structures and external interface for MediaTek PLL frequency-hopping support layered over the normal PLL clock implementation.

Important APIs and types: `struct fh_pll_state` stores FHCTL base, enable state, and SSC rate. `struct fh_pll_data` describes per-PLL FHCTL identity, version, register offset, DDS mask, slopes, enable bits, trigger bits, delta fields, and update limit shift. `struct mtk_pllfh_data` combines mutable state with constant descriptor data. `struct fh_pll_regs` stores resolved FHCTL register pointers. `struct mtk_fh` embeds `struct mtk_clk_pll` and adds FH registers, descriptor pointer, operation table, and lock. `struct fh_operation` defines `hopping()` and `ssc_enable()` callbacks.

Control flow: the header itself only declares interfaces. Runtime flow is implemented by `clk-pllfh.c`: parse FHCTL DT state, initialize `struct mtk_fh` register pointers from FHCTL offset tables, register clocks with PLL operations that call FH hopping for rate changes, and unregister mixed FH/non-FH PLLs.

State and persistence: FH state is transient and lives in `mtk_pllfh_data.state`, FHCTL registers, and `struct mtk_fh`. The constant `fh_pll_data` descriptors are compiled into SoC drivers.

Dependencies and integration points: the header includes `clk-pll.h` because FH PLLs embed the normal MediaTek PLL object and reuse PLL prepare/recalc/rate-calculation helpers. It is consumed by SoC drivers that provide FH descriptor arrays and by FHCTL helper code.

Risks: descriptor values are highly hardware-specific; a bad `fh_ver`, `fhx_offset`, mask, slope, or trigger bit may cause rate changes to hang or program an unintended PLL. `fh_enable` is mutable and set by DT parsing, so initialization order matters. The API assumes callers pass arrays whose PLL IDs correspond to the normal PLL descriptor IDs.

Test signals: test by building FH-enabled SoC drivers, booting with and without FHCTL DT nodes, checking FH-enabled PLLs use hopping on rate changes, confirming SSC configuration is applied when requested, and validating unregister cleanup does not leave FHCTL mappings or registered clocks behind.
