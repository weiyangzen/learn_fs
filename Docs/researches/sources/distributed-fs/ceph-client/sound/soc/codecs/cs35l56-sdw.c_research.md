# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-sdw.c

Purpose: SoundWire binding for CS35L56/CS35L57/CS35L63 ASoC devices. It adapts SoundWire register access and lifecycle events to the shared CS35L56 core.

Important APIs and data: custom regmap bus `cs35l56_regmap_bus_sdw` implements read, write, and gather-write with address offset `0x8000`, endian conversion, SoundWire page splitting, and slow OTP-register reads through bridge status/data registers. `cs35l56_sdw_read_prop()` declares playback/capture ports, paging support, quirks, interrupt masks, and optional clock-stop-mode1 support. `cs35l56_sdw_ops` wires property, interrupt, status, and clock-stop callbacks. Probe selects `cs35l56_regmap_sdw` or `cs35l63_regmap_sdw`, starts regcache cache-only until enumeration, calls `cs35l56_common_probe()`, and defers full init until attach.

Control flow: SoundWire attach status triggers `cs35l56_sdw_init()` if not initialized or soft-resetting. That gets the unique ID, uses it as calibration index if none was set, runs `cs35l56_init()`, and enables SoundWire codec IRQs when init is complete. Interrupt callback masks and clears implementation-defined interrupts, holds runtime PM, and queues `cs35l56_sdw_irq_work()`, which calls the shared `cs35l56_irq()` and unmasks unless removal/suspend asked not to. Runtime resume handles clock-stop/unattach completion before shared resume and interrupt re-enable. System suspend disables and flushes SoundWire IRQ work before delegating shared suspend.

State and persistence: private state includes SoundWire peripheral pointer, link/unique IDs, attach flags, clock-stop-mode1 flag, IRQ work item, and unmask suppression flag. Regcache starts cache-only because registers are unavailable until SoundWire enumeration completes.

Dependencies and integration: depends on SoundWire core APIs, regmap, PM runtime, workqueues, endian helpers, and shared CS35L56 core/shared namespaces. It integrates with SoundWire manager lifecycle rather than a fixed platform IRQ.

Risks: endian and page-boundary handling are central; mistakes corrupt firmware controls or register values. Slow OTP reads poll bridge status and can timeout. PM reference balancing around queued IRQ work is delicate; canceling instead of flushing could leak a runtime PM get, which the code comments explicitly avoid in suspend. Register access is impossible during clock-stop/unattach, so resume must wait for `initialization_complete`.

Test signals: SoundWire enumeration attach/unattach, clock-stop-mode1 suspend/resume, OTP slow-read paths, multi-page regmap reads/writes, queued interrupt handling and PM balance, and device IDs for CS35L56/57/63.
