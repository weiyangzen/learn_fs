# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.c

Purpose: shared helper implementation for AMD powerplay hwmgr code: voltage conversions, PPT table copying, register polling, DPM table utilities, EVV lookup, thermal IRQ handling, SMU9 IRQ registration, AtomBIOS table lookup, PPT v1 dependency copying, and SOC15 watermark programming.

Important APIs and functions: `convert_to_vid()` / `convert_to_vddc()` implement the 6200/25 SVI2 conversion. `phm_copy_clock_limits_array()` and `phm_copy_overdrive_settings_limits_array()` allocate endian-converted arrays. Register wait helpers poll direct/indirect registers against `hwmgr->usec_timeout`. Voltage helpers trim duplicates, derive MVDD/VDDCI/VDD tables, clamp table size, find voltage IDs/indexes, closest VDDCI, boot DPM levels, and EVV voltage for SCLK. DPM helpers reset tables, set PCIe entries, and compute enable masks. `phm_irq_process()` handles thermal and critical temperature interrupts, scheduling SW CTF work or calling `orderly_poweroff(true)`. `smu9_register_irq_handlers()` registers THM and SMUIO GPIO19 sources. `smu_set_watermarks_for_clocks_ranges()` writes DAL watermark ranges to firmware table rows.

Control flow and state: most helpers transform caller-owned tables or poll hardware. IRQ processing branches by legacy/SOC15 client/source IDs. Allocation helpers transfer ownership to caller pointers; voltage trimming rewrites the caller table; IRQ registration allocates an IRQ source.

Dependencies and integration: used across many hwmgr backends. Depends on AtomBIOS helpers, PPT v1 structures, CGS register access, AMDGPU IRQ/delayed work, Linux reboot API, endian helpers, and thermal source IDs.

Risks and test signals: `phm_get_lowest_enabled_level()` has no zero-mask guard; some lookup assertion failures return `0`, which can be a valid index; wait helpers use inconsistent error codes; critical thermal IRQ powers off the system. Test voltage/table helpers, EVV branches by ASIC generation, register waits, IRQ registration/injection, and invalid watermark counts.
