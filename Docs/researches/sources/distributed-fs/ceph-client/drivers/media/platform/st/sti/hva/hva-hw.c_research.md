# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.c

Purpose: implements the low-level HVA hardware interface: MMIO resource setup, clocks/runtime PM, IRQ handling, task FIFO submission, hardware version detection, and optional register dumping.

Important APIs and functions: exported APIs are `hva_hw_probe`, `hva_hw_remove`, `hva_hw_runtime_suspend`, `hva_hw_runtime_resume`, `hva_hw_execute_task`, and debugfs-only `hva_hw_dump_regs`. IRQ handlers cover status completion and hardware memory-interface errors.

Control flow: probe maps registers, records ESRAM resource address/size, prepares the clock, installs status and error threaded IRQs, disables them until task execution, initializes mutex/completion, enables runtime PM, and reads the IP version. Runtime resume enables the clock and sets it to 300 MHz; suspend disables it. `hva_hw_execute_task` serializes with `protect_mutex`, enables IRQs, resumes PM, enables command-specific clock gating, programs byte-swap and memory-interface registers, pushes command/client id and task descriptor physical address to the FIFO, waits up to 2 seconds for completion, maps interrupt-reported `ctx->hw_err` to return status, disables IRQs/gating, and autosuspends PM.

State and persistence: `hva_dev` stores registers, ESRAM range, clock, IRQ numbers, completion, hardware status/error registers, IP version, and context slots. `hva_ctx->hw_err` and error counters are updated by IRQ threads. Hardware register state is programmed per task and gated off afterward.

Dependencies and integration points: depends on platform resources, two IRQ lines, runtime PM, clocks, `hva.h` context/device helpers, and task descriptors produced by codec backends such as `hva-h264.c`.

Risks: `hva_hw_get_ip_version` unlocks `protect_mutex` on PM failure even though this function did not lock it, which is dangerous on that error path. Probe resumes PM and then calls `hva_hw_get_ip_version`, which itself takes/puts PM, making PM reference accounting worth reviewing. IRQs are disabled/enabled for every task; missed completions or shared IRQ semantics can deadlock the 2-second wait. Task addresses are passed directly from DMA metadata, so DMA mask/IOMMU setup in the V4L2 layer is critical.

Test signals: probe on valid/invalid HVA versions, runtime suspend/resume cycles, forced status and memory-interface error IRQs, FIFO timeout path, multi-context serialization, clock-rate failure injection, and debugfs register reads while suspended.
