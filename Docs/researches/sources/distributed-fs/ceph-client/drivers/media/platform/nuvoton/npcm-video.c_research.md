# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-video.c

## Purpose
`npcm-video.c` implements the Nuvoton NPCM BMC video capture driver. It exposes the VCD capture/differentiation engine as a V4L2 capture device and optionally uses the ECE block to output changed rectangles in HEXTILE format.

## Important APIs, Types, and Functions
Core state types are `struct npcm_video`, `struct npcm_ece`, `struct npcm_video_buffer`, `struct npcm_video_addr`, and rectangle-list helpers. Hardware helpers include `npcm_video_init_reg()`, `npcm_video_vcd_ip_reset()`, `npcm_video_vcd_state_machine_reset()`, `npcm_video_gfx_reset()`, `npcm_video_detect_resolution()`, `npcm_video_set_resolution()`, and `npcm_video_start_frame()`. Encoding helpers include `npcm_video_ece_*()`, `npcm_video_raw()`, and `npcm_video_hextile()`. V4L2/vb2 operations cover format, DV timings, input status, custom NPCM controls, open/release, queue setup, buffer prepare/queue/finish, streaming start/stop, and the threaded IRQ `npcm_video_irq()`.

## Control Flow
Probe allocates driver state, maps VCD registers, gets reset, resolves GCR/GFXI syscons, maps the IRQ, initializes reserved memory and DMA mask, optionally initializes ECE from a phandle, then registers V4L2 controls, vb2 queue, and `/dev/video0`. On first open, `npcm_video_start()` initializes registers, allocates a coherent VCD source framebuffer, detects active host resolution, programs line pitch and frame-buffer addresses, and prepares ECE if available. Streaming starts by taking queued buffers and issuing a capture or compare command. The IRQ clears status, completes capture buffers by copying RGB565 or encoding HEXTILE rectangles, updates payload/timestamp/sequence, removes the buffer from the queue, and starts the next frame. Resolution-change interrupts mark the queue errored and emit a source-change event; FIFO errors restart capture. Stop disables interrupts/mode, frees framebuffer and rectangle tables, resets controls, and stops ECE on last client.

## State and Persistence
`struct npcm_video` stores V4L2 format, active/detected timings, input status, queued buffers, flags for streaming/capturing/resolution-change/stopped, sequence, source framebuffer, ECE client count, rectangle lists/counts, current capture command, and last operation. Hardware register state is rebuilt on open/start and cleared on stop. Reserved DMA memory may be provided by DT but no driver data persists across removal.

## Dependencies and Integration Points
The driver depends on V4L2, vb2 DMA-contig, custom UAPI controls from `uapi/linux/npcm-video.h`, syscon regmaps for `nuvoton,sysgcr` and `nuvoton,sysgfxi`, reset controls, reserved memory, IRQ handling, and optional ECE platform device phandle `nuvoton,ece`. Compatibles are `nuvoton,npcm750-vcd` and `nuvoton,npcm845-vcd`.

## Risks and Edge Cases
Probe uses `kzalloc_obj()` without devm/free cleanup on early failures, so error-path ownership should be checked before edits. `dev_get_drvdata()` in remove expects the V4L2 device drvdata path to be valid; setup changes must keep driver data consistent. HEXTILE output depends on rectangle-list allocation and ECE polling; failures can produce zero-sized payloads. Resolution change intentionally errors the vb2 queue, so userspace must re-query timings. Source framebuffer allocation failure leaves open partially initialized unless callers observe input status and subsequent cleanup.

## Test Signals
Test RGB565 and HEXTILE capture, complete and diff capture modes, queued-buffer starvation, min/max DV timings, source-change events, FIFO overrun recovery, ECE unavailable DT path, ECE rectangle count control updates on dequeue, reserved memory and 32-bit DMA mask handling, and open/release reference behavior.
