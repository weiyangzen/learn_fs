# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_drif.c

## Purpose
`rcar_drif.c` implements the R-Car Gen3 Digital Radio Interface as a V4L2 SDR capture driver. DRIF is receive-only, clocked by an external tuner/master, and uses SYS-DMAC to move FIFO samples to memory. One or two internal channels can be bonded; the driver exposes a single SDR video node after an async tuner subdevice binds.

## Important APIs, Types, And Functions
Core state types are `struct rcar_drif` for one internal hardware channel, `struct rcar_drif_sdr` for the grouped SDR device, `struct rcar_drif_hwbuf` for coherent DMA chunks, `struct rcar_drif_frame_buf` for userspace vb2 buffers, and `struct rcar_drif_format` for SDR formats. Main functions cover DMA channel allocation, coherent buffer allocation, MDR format programming, cyclic DMA queueing, RX start/stop, vb2 callbacks, SDR ioctls, tuner ioctl forwarding, async notifier callbacks, DT endpoint/bonding parsing, probe/remove, and stub PM callbacks.

## Control Flow
Probe creates one channel, gets clock and MMIO, records the FIFO physical base, and checks optional `renesas,bonding`. A non-primary bonded device only records channel 1 and waits for the primary. The primary allocates `rcar_drif_sdr`, links one or two channels, chooses a default format matching available channels, initializes vb2 with vmalloc-backed userspace buffers, registers `v4l2_device`, parses a tuner endpoint, and registers an async notifier. On notifier completion it imports tuner controls, registers subdev nodes, and registers the SDR video node.

On stream start, clocks are enabled, MDR defaults and selected format are written, DMA slave channels are requested/configured, coherent cyclic DMA buffers are allocated, each active channel is reset and submitted as cyclic DMA, status bits and DMA request interrupts are enabled, RX is enabled and polled, and `produced` resets. DMA callbacks serialize on `dma_lock`, mark channel buffer completion/overflow, wait for both bonded channel buffers when needed, copy hardware data into the next queued vb2 buffer, timestamp/sequence it, set payload, and complete it done or error. Stop disables RX, terminates DMA, returns queued vb2 buffers as error, frees coherent buffers, releases DMA channels, and disables clocks.

## State And Persistence
Runtime state includes channel mask from DT, current channel mask from selected format, current format pointer, MDR1 sync polarity/mode from endpoint properties, coherent hardware buffers, DMA handles, queued vb2 buffers, `produced` sequence, tuner subdev pointer, and controls copied from the tuner. No persistent storage exists. Suspend/resume are currently no-ops.

## Dependencies And Integration Points
The driver depends on platform devices, OF graph/phandle parsing, clocks, DMAengine cyclic transfers, coherent DMA memory, V4L2 async/control/device/event/ioctl frameworks, and vmalloc vb2 memory. It integrates with an external tuner subdevice for frequency/tuner ioctls and control handling, and with DT properties `sync-active`, `renesas,bonding`, and `renesas,primary-bond`.

## Risks
PM suspend/resume is explicitly unimplemented, so active streaming across system sleep is risky. Hardware DMA buffers are copied into vmalloc vb2 buffers, adding CPU cost and possible latency under high sample rates. If userspace queues too slowly, samples are dropped and sequence gaps appear. Bonded two-channel capture depends on synchronized DMA callbacks and status flags; races are mitigated by `dma_lock` but need stress testing. DMA buffer allocation error cleanup may leave earlier channel allocations to cleanup paths only. Tuner subdevice absence means no SDR node is registered.

## Test Signals
Validate single and bonded DT configurations, primary/non-primary probe ordering and defer behavior, tuner async bind/unbind, SDR node creation, all three PCU formats, one-channel selection when format needs fewer channels than hardware, cyclic DMA start/stop, overflow error completion, slow-consumer sequence gaps, clock/DMA cleanup on failures, streamoff buffer states, and suspend/resume expectations.
