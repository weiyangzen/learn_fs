# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.c

Purpose: low-level AMD ACP hardware management: DMA descriptors, PSP/SHA firmware validation, scratch access, power/reset/init, IRQ handling, SoundWire probing/wake handling, SOF probe/remove, and PM.

Important APIs/types/functions: `configure_and_run_dma()`, `configure_and_run_sha_dma()`, `acp_dma_status()`, `memcpy_from_scratch()`, `memcpy_to_scratch()`, `amd_sof_acp_suspend()`, `amd_sof_acp_resume()`, `amd_sof_acp_probe()`, and `amd_sof_acp_remove()` are exported/common callbacks. Internal helpers handle DMA descriptor programming, PSP mailbox commands, ACP power-on/reset/DSP-reset, memory init, IRQ top/thread handlers, SoundWire ACPI scan/probe/exit, and ACP70 wake events. DMI quirk `Valve Galileo` enables signed firmware and related behavior.

Control flow: probe allocates `acp_dev_data`, registers a `dmic-codec` platform device, maps BAR0, powers/resets/init ACP, requests threaded IRQ, optionally scans/probes SoundWire, defines mailbox/debug box offsets, applies DMI quirks, initializes memory and stream slots. IRQ top half handles DSP software interrupt, SoundWire IRQs, ACP error IRQs, and ACP70 wake/PME status; DSP IPC work is delegated to the thread after acquiring hardware semaphore. Suspend resets ACP or only DSP when SoundWire clock-stop is active; resume reinitializes or performs DSP reset based on saved SoundWire state.

State and persistence: `acp_dev_data` stores device pointer, firmware DMA buffers, mutex, SoundWire info/context, descriptors, stream pool, trace/probe stream pointers, quirk pointer, debug flag, PCI revision, and SoundWire wake/status booleans. Scratch mailbox content and hardware registers persist in ACP SRAM/registers across parts of the lifecycle.

Dependencies and integration points: PCI, platform device registration, AMD SMN/PSP mailbox functions, SoundWire AMD APIs, SOF ops/core, ACP descriptors, DMI, IRQ subsystem, DMA, runtime/system PM.

Risks: hardware sequencing is revision-sensitive. `configure_and_run_dma()` loops while `dsp_data_size >= 0`, which can produce a zero-length final descriptor when size is page-aligned. Scratch copy helpers operate in 32-bit units and assume aligned byte counts. SoundWire IRQ paths assume `adata->sdw` and `pdev[]` are valid when SDW status bits occur. Error paths must unregister DMIC/IRQ consistently.

Test signals: ACP power/reset polling, firmware SHA validation, DMA completion, IPC interrupt handling, SoundWire link discovery and wake, suspend/resume with and without clock-stop, DMI signed firmware path, and remove cleanup.
