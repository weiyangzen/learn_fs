<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-st.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-st.c

## Purpose
Sidetone support for OMAP3 McBSP ports. It manages sidetone FIR coefficients, channel gains, sysfs taps, ALSA mixer controls, and hardware enable/disable sequencing alongside the main McBSP stream state.

## APIs, Types, and Functions
`struct omap_mcbsp_st_data` holds sidetone MMIO, optional interface clock, running/enabled flags, 128 FIR taps, tap count, and two signed gains. Exported functions are `omap_mcbsp_st_init()`, `omap_mcbsp_st_start()`, `omap_mcbsp_st_stop()`, and `omap_mcbsp_st_add_controls()`. Internal helpers program sidetone core registers, FIR taps, gains, sysfs `st_taps`, and controls for McBSP2/McBSP3.

## Control Flow, State, and Persistence
Init is optional: if no `sidetone` memory resource exists it returns success without sidetone state. When present it maps sidetone registers, gets optional `ick`, creates the `st_taps` sysfs group, and attaches state to `mcbsp`. Enabling sidetone sets `enabled`, starts if possible, writes all 128 FIR coefficients, writes gains, disables autoidle, enables McBSP SSELCR sidetone and sidetone-core enable bits, and may force the interface clock on through platform data. Stop reverses enable bits and autoidle. ALSA controls persist signed gain and switch state; sysfs persists current FIR taps in memory.

## Dependencies and Integration
Depends on the main McBSP private state, platform `force_ick_on` callback, ASoC DAI controls, sysfs device attributes, and McBSP2/3 port IDs. Main `omap-mcbsp.c` invokes start/stop around stream start/stop.

## Risks and Test Signals
Risks include parsing unlimited comma-separated tap input without checking `i < 128`, polling FIR write completion with no delay, controls only for ports 2 and 3, possible sleep/clock callbacks under spinlock, and sidetone start depending on `mcbsp->free`. Test signals are sidetone resource absent/present probe, sysfs tap validation, gain control updates while enabled, McBSP2/3 controls, FIR load completion, stream start/stop clock gating, and no lockdep warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-st.c -->
