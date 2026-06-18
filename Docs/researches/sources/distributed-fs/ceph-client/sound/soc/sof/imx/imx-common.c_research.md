# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.c

Purpose: common NXP i.MX SOF hardware ops for IPC, memory mapping, clocks/power domains, suspend/resume, panic dumps, and generic i.MX DSP probe/remove.

Important APIs/types/functions: exported `imx8_dump()` and `sof_imx_ops`. Internal functions handle Xtensa oops reads, IPC request/reply callbacks, mailbox send, BAR/mailbox/window lookup, power-state bookkeeping, runtime/system PM, memory-region parsing from resources/reserved memory, IPC platform device registration, and cleanup.

Control flow: probe creates an `imx-dsp` platform device, optionally binds reserved DMA memory, registers devres cleanup, obtains IPC handle, maps memory regions declared by chip info, attaches power domains if needed, gets/enables clocks, installs IPC ops, sets mailbox BAR and boot mailbox offset, then calls chip-specific probe. IPC request checks panic code when supported before dispatching SOF messages. Suspend shuts down chip core, frees MU channels, disables clocks, and sets D3; resume reenables clocks, requests channels, normalizes runtime PM state if needed, and sets D0.

State and persistence: `imx_common_data` in `sdev->pdata->hw_pdata` stores IPC device/handle, clocks, power domains, and chip private data. `sdev->bar[]`, mailbox settings, and DSP power state are initialized here.

Dependencies and integration points: i.MX firmware DSP IPC, OF resources/reserved memory, power domains, clocks, SOF OF device layer, SOF mailbox/block helpers, Xtensa panic helpers, and chip ops from `imx8.c`/`imx9.c`.

Risks: resource names in device tree must match chip memory descriptors. Probe defers if IPC handle is not ready. Clock/channel handling must be balanced across PM and remove. `imx_get_bar_index()` only accepts IRAM/SRAM, so DRAM mappings are not usable through that callback.

Test signals: OF probe with memory resources/reserved memory, IPC doorbell round trips, firmware boot, panic dump, runtime/system suspend/resume, and remove cleanup.
