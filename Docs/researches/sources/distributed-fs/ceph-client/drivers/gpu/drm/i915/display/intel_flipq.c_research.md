# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.c

Purpose: implements DMC firmware flip queues, allowing i915 to enqueue DSB command buffers for execution at presentation timestamps on supported platforms.

Important APIs/types/functions: public functions include `intel_flipq_supported()`, `intel_flipq_init()`, `intel_flipq_reset()`, `intel_flipq_enable()`, `intel_flipq_disable()`, `intel_flipq_add()`, `intel_flipq_exec_time_us()`, `intel_flipq_wait_dmc_halt()`, `intel_flipq_unhalt_dmc()`, and `intel_flipq_dump()`. Internal helpers compute queue offsets/sizes, entry sizes, execution time, preempt timeout, current head, tail writes, DMC wake, and Lunar Lake/Panther Lake queue-entry formats.

Control flow: init waits for DMC firmware and records per-CRTC queue MMIO starts. Enable programs scanline compare windows before vblank, enables the relevant pipe DMC event, and turns on queue control. Add checks ring space, converts relative PTS to DMC timestamp domain, preempts the queue, writes one entry in the per-platform format, advances software tail, atomically updates all hardware tail pointers, unpreempts, and wakes DMC. Disable preempts, disables control/event, and clears scanline compares. Reset clears hardware head/tail pointers and software tails.

State and persistence: each `intel_crtc` stores `flipq[]` metadata including `start_mmioaddr`, `flipq_id`, and software `tail`. Hardware queue RAM, head/tail pointers, timestamp, scanline compares, and DMC event enables persist until reset/disable. Supported state depends on module param, DMC firmware, display version, and VRR timing generator policy.

Dependencies and integration: integrates with pipe DMC firmware/registers, DSB command buffers, CRTC state/mode timing, CDCLK/SAGV timing, VRR policy, display workarounds, and MMIO helpers.

Risks: queue overflow detection depends on synchronized head/tail state. Incorrect execution-time estimates can schedule too close to vblank. Platform entry layouts differ between LNL and PTL. Preempt timeouts indicate DMC did not halt in time. Feature support depends on firmware and VRR timing-generator assumptions.

Test signals: run on supported display versions with DMC loaded, enqueue plane/general DSB updates, exercise reset/enable/disable, queue overflow warnings, timestamp scheduling, VRR configurations, DMC preempt timeout injection, and debug dumps.
