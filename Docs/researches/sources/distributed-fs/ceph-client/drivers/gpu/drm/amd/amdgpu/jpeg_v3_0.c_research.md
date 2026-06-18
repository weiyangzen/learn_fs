# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.c

Purpose: implements a single-instance JPEG v3.0 IP block that largely reuses v2.0 packet helpers while adapting power gating, clock gating, harvesting checks, tiling registers, and reset behavior for VCN 3.x hardware.

Important APIs and functions: exports `jpeg_v3_0_ip_block`. Lifecycle functions perform early/sw/hw init, fini, suspend/resume, idle/wait, clockgating, powergating, and ring reset. The ring function table reuses `jpeg_v2_0_dec_ring_*` helpers and `amdgpu_jpeg_dec_parse_cs`.

Control flow and state: early init skips harvesting checks for IP versions 3.1.1/3.1.2 but otherwise returns `-ENOENT` if JPEG is disabled. SW init registers the v2 decode IRQ source, initializes shared JPEG state, creates a doorbell ring, register dump, and reset sysfs. Start enables DPM JPEG, disables static power gating, disables CGC, sets decode and encode GFX10 tiling, enables JMI/interrupts, and programs JRBC ring registers. Stop resets JMI, gates clocks/power, and disables DPM.

Dependencies and integration: depends on VCN 3.0 register headers, shared v2.0 packet functions, amdgpu JPEG helpers, DPM, NBIO doorbell ranges, SOC15 wait/access helpers, and reset mask infrastructure.

Risks and test signals: static power gating relies on PGFSM waits and anti-hang bit sequencing. The generation uses v2 IRQ source IDs despite v3 register headers. Test signals include harvest handling per IP version, ring and IB tests, per-queue reset availability outside SR-IOV, clockgating returning `-EBUSY` when not idle, and successful register dump/sysfs reset mask setup.
