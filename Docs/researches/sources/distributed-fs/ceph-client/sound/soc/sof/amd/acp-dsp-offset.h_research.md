# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-dsp-offset.h

Purpose: register offset map for AMD ACP DMA, DSP, ATU, PGFSM, interrupt, SHA, scratch, cache, SoundWire, and wake/PME blocks.

Important APIs/types/functions: defines offsets for generic ACP DMA registers and ACP70-specific DMA layout, `ACP_DSP0_RUNSTALL`, ATU groups, soft reset/control, per-generation PGFSM/clkmux, interrupt status/control, hardware semaphores, I2S error reason registers, SHA DMA/PSP registers, scratch base, fusion runstall, cache windows, and ACP70 SoundWire wake/PME bits.

Control flow: no executable flow. These constants drive register programming in `acp.c`, firmware loading in `acp-loader.c`, IPC in `acp-ipc.c`, and stream PTE setup in `acp-stream.c`.

State and persistence: none directly. Constants represent hardware state addresses.

Dependencies and integration points: shared by all AMD ACP platform drivers and descriptor files. Per-chip descriptors select which offsets apply for each revision.

Risks: wrong offsets cause hardware misconfiguration, failed DMA, broken interrupts, or invalid power transitions. ACP70 has several register layout differences, so callers must branch correctly by PCI revision.

Test signals: hardware boot/probe success, DMA transfer completion, interrupt handling, SoundWire wake handling, and firmware trace/probe stream operation across supported ACP generations.
