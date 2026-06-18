# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.c

Purpose: common Cedrus hardware management: engine mode selection, capture output format register programming, IRQ handling, watchdog timeout recovery, runtime PM suspend/resume, and platform hardware resource acquisition/release.

Important APIs/functions: `cedrus_engine_enable()` writes `VE_MODE` based on source codec, width flags, DDR mode, and write mode. `cedrus_engine_disable()` disables the engine. `cedrus_dst_format_set()` configures tiled or untiled capture layout registers. `cedrus_irq()` cancels watchdog, gets current context, dispatches codec IRQ status/clear/disable, and completes the mem2mem job. `cedrus_watchdog()` resets hardware and completes the job as error after timeout. `cedrus_hw_suspend()` disables clocks and asserts reset; `cedrus_hw_resume()` resets hardware and enables AHB/MOD/RAM clocks. `cedrus_hw_probe()` obtains variant data, IRQ, reserved memory, SRAM, clocks, reset, MMIO, module clock rate, and runtime PM. `cedrus_hw_remove()` disables PM and releases SRAM/reserved memory.

Control flow: core probe calls `cedrus_hw_probe()` before registering V4L2 nodes. Streaming output queue calls runtime PM resume through `cedrus_video.c`, which invokes `cedrus_hw_resume()` as needed. Decode jobs enable engine and start hardware; completion happens through IRQ or watchdog.

State and persistence: global hardware state in `cedrus_dev`: capabilities, MMIO base, clocks, reset control, delayed watchdog work. Runtime PM owns clock/reset lifetime.

Dependencies/integration: uses Linux clk, reset, IRQ, PM runtime, OF reserved memory, DMA mapping, sunxi SRAM, V4L2 mem2mem, and codec ops. Register macros come from `cedrus_regs.h`.

Risks: watchdog reset does not call codec-specific IRQ clear/disable and may leave registers in a reset-dependent state. IRQ handler assumes watchdog cancellation tells whether job already timed out. `platform_get_irq()` treats IRQ 0 as failure due `<= 0`, which matches older conventions but can be problematic on systems where IRQ 0 is valid. Output format programming for tiled uses `VE_CHROMA_BUF_LEN` with an output-format constant, which is hardware-specific and easy to misread.

Test signals: runtime PM cycle tests, IRQ completion for all codecs, watchdog timeout injection, reserved memory absent/present, SRAM claim failure, clock rate failure, streamon/streamoff clock balance, and tiled versus untiled capture format register validation.
