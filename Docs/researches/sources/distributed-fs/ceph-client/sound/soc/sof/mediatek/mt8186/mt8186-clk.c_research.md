# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.c

Purpose: Handles MT8186 ADSP clock lookup and on/off sequencing.

Important APIs: `mt8186_adsp_init_clock()` allocates `priv->clk` and resolves `"audiodsp"` and `"adsp_bus"`. `mt8186_adsp_clock_on()` enables both clocks, then writes `ADSP_CK_EN` and `ADSP_UART_CTRL` bits for UART, DMA, timer, core debug, core clock, UART bus clock gate, and UART reset. `mt8186_adsp_clock_off()` clears those registers and disables clocks in reverse order.

Control flow: Enable first prepares `audiodsp`, then `adsp_bus`, rolling back `audiodsp` if the second enable fails. Clock-on performs register writes only after both clocks are active. Clock-off clears hardware enable bits before disabling the Linux clock handles.

Dependencies and integration: Uses `adsp_priv` from `sdev->pdata->hw_pdata`, common SOF register IO, and MT8186 register definitions. Called from MT8186 probe, suspend, resume, remove, and error paths.

State and persistence: Clock handles are devm-managed; enable state is runtime state balanced manually by probe/resume versus suspend/remove/error unwind.

Risks: Unbalanced clock off on partially enabled paths would call disable on disabled clocks; current helper rollback covers the second-enable failure. Register writes require mapped DSP_REG_BAR and clocks already active. Device tree clock names must match exactly.

Test signals: Missing clock names, failure enabling each clock, probe error unwind after clock on, suspend/resume cycles, and register traces showing enable bits cleared on removal.
