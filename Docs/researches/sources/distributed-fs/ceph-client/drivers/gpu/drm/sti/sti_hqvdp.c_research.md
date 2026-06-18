# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp.c

Purpose: Implements the HQVDP video processing plane. It exposes an NV12 overlay plane backed by an XP70 firmware processor, command-mailbox DMA buffers, scaling coefficient LUTs, deinterlacing setup, and VTG-driven bottom-field handling.

Important APIs/functions: `sti_hqvdp_probe()` maps registers, gets `hqvdp` and `pix_main` clocks, deasserts reset, resolves VTG, and registers component ops. `sti_hqvdp_bind()` creates the DRM plane. `sti_hqvdp_start_xp70()` requests `hqvdp-stih407.bin`, validates its header sizes, resets hardware, loads plug/PMEM/DMEM firmware sections, enables fetch, and waits for firmware ready. `sti_hqvdp_atomic_check()` validates DMA backing, sizes, scaling capability, starts firmware if needed, and registers VTG. `sti_hqvdp_atomic_update()` fills a free command with source addresses, pitches, viewport, output size, CSDI/deinterlace settings, HVSRC coefficients, and posts it to `HQVDP_MBX_NEXT_CMD`.

Control flow: Two command buffers are shared with firmware; free/current/next helpers avoid overwriting active commands. Interlaced input posts a top-field command and marks bottom-field pending; the VTG callback clones the current command, adjusts luma/chroma by half-pitch, posts a bottom-field command, and updates field FPS. Disable is synchronized by VTG flush and waits for firmware idle before dropping the pixel clock.

State/persistence: `struct sti_hqvdp` stores command DMA memory, physical base, XP70 initialized flag, VTG registration flag, pending bottom-field flag, clocks, reset, and embedded STI plane state.

Dependencies/integration: Uses DRM atomic plane helpers, firmware loader, DMA GEM helpers, compositor/mixer/VTG integration, `sti_hqvdp_lut.h` coefficient tables, and debugfs command/mailbox dumps.

Risks/test signals: Firmware absence leaves the plane unable to start but `atomic_check()` continues after calling start unless later state exposes failure. Preallocated command buffers are never explicitly freed in remove. Scaling math divides by destination dimensions, so zero-sized states depend on earlier DRM validation. Test firmware load errors, NV12-only format, scaling limits, interlaced bottom-field posting, VTG unregister, mailbox debugfs, and disable idle timeout.
