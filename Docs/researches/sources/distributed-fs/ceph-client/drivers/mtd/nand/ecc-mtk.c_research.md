# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mtk.c

Purpose: drives MediaTek NAND ECC hardware blocks and exports helper APIs used by MediaTek NAND controllers to configure, enable, wait for, and query encode/decode operations.

Important APIs and types: key structures are `mtk_ecc_caps` for SoC register layout and strength tables, and `mtk_ecc` for device state, registers, clock, completion, mutex, sector mask, and parity buffer. Exported APIs include `of_mtk_ecc_get()`, `mtk_ecc_release()`, `mtk_ecc_enable()`, `mtk_ecc_disable()`, `mtk_ecc_wait_done()`, `mtk_ecc_encode()`, `mtk_ecc_get_stats()`, `mtk_ecc_adjust_strength()`, and `mtk_ecc_get_parity_bits()`.

Control flow: probe allocates state, chooses compatible-specific caps, maps registers, gets the clock and IRQ, sets a 32-bit DMA mask, and installs the IRQ handler. Consumers acquire the engine through a `nand-ecc-engine` or legacy `ecc-engine` phandle; acquisition enables the clock and initializes hardware idle/disabled state. `mtk_ecc_enable()` locks the engine, waits idle, programs encode/decode config, arms interrupts when needed, and starts the selected operation. Encode maps the data buffer for DMA, enables the encoder, waits for completion, copies generated parity registers into the caller buffer, unmaps DMA, and disables/unlocks. Decode completion is signaled by IRQ and stats are later read from decode enumeration registers.

State and persistence: state is runtime-only: register programming, clock state, completion, mutex ownership, and per-operation sector mask. ECC bytes become persistent only when the NAND controller writes them to OOB.

Dependencies and integration points: depends on platform devices, OF matching for `mediatek,*-ecc`, clocks, IRQs, DMA mapping, I/O polling, and `<linux/mtd/nand-ecc-mtk.h>`. It is a provider library for host controller drivers, not a generic `nand_ecc_engine` registration.

Risks and test signals: risks include strength table selection, IRQ status clearing, timeout paths unlocking the mutex, DMA map/unmap balance, and suspend/resume clock transitions. Tests should cover each compatible caps table, invalid strength rejection, NFI versus non-NFI modes, encode timeout and success, decode stats for corrected/failed sectors, phandle probe defer, clock enable failure, and concurrent callers serialized by the mutex.
