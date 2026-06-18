# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c

Purpose: implements JPEG v4.0.5/v4.0.6 support with one or two instances, optional DPG mode programming, per-instance doorbells, v4 IRQ handling, and reuse of v2 packet helpers.

Important APIs and functions: exports `jpeg_v4_0_5_ip_block`. Early init selects one instance for UVD 4.0.5 and two for 4.0.6. DPG-specific helpers `jpeg_v4_0_5_start_dpg_mode()` and `_stop_dpg_mode()` program JPEG DPG SRAM/registers, while normal start/stop handle static power gating, CGC, JMI, interrupts, and JRBC ring setup. Ring reset restarts the whole JPEG block.

Control flow and state: sw init registers decode and poison source IDs on each live instance, initializes shared JPEG state, creates one doorbell ring per non-harvested instance, sets pitch mappings, register dumps, and reset sysfs. HW init skips ring tests when `AMD_PG_SUPPORT_JPEG_DPG` is set; otherwise it tests each live ring. Start programs NBIO/VCN doorbells for each playback, then chooses DPG or normal register programming. State includes `harvest_config`, per-ring `me`, block-wide `cur_state`, `indirect_sram`, and DPG SRAM current-address pointers.

Dependencies and integration: depends on VCN 4.0.5 register headers, `mmsch_v4_0.h`, amdgpu JPEG helpers, DPM, NBIO doorbells, SOC15 JPEG DPG write macros, PSP SRAM update helper, and shared v2.0 ring packet helpers.

Risks and test signals: poison interrupts are registered against the same IRQ object as decode, so the interrupt handler must distinguish source IDs and call `amdgpu_jpeg_process_poison_irq()`. `wait_for_idle()` returns after the first non-harvested instance, so later instances are not waited on. DPG mode currently skips ring tests, reducing boot-time validation. Test signals include UVD 4.0.5 vs 4.0.6 instance selection, harvested skips, DPG direct and indirect SRAM paths, PSP SRAM update, two-client interrupt routing, poison IRQ processing, and reset under DPG and non-DPG modes.
