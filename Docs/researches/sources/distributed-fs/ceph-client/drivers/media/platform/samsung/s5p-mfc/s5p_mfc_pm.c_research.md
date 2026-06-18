# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.c

Purpose: implements runtime power-management and clock-control helpers for the S5P MFC device.

Important APIs and functions: `s5p_mfc_init_pm` acquires variant clocks and enables runtime PM. `s5p_mfc_final_pm` disables runtime PM. `s5p_mfc_clock_on`/`s5p_mfc_clock_off` gate the selected software clock gate. `s5p_mfc_power_on` resumes the device and prepares/enables all clocks. `s5p_mfc_power_off` re-enables the gate clock, disables/unprepares all clocks, and drops the runtime PM reference.

Control flow: probe initializes `dev->pm` from variant clock names and device pointers, treating missing additional clocks as optional. Power-on resumes runtime PM, enables clocks in order, and rolls back already enabled clocks on failure. After enabling, it disables `clock_gate` so scheduler paths can explicitly enable/disable it around hardware operations. Power-off reverses this by enabling `clock_gate` before disabling all prepared clocks.

State and persistence: `dev->pm` stores clock count, names, clock pointers, runtime PM device, and optional `clock_gate`. Clock and PM state persists while the device is bound and changes during hardware scheduling, suspend/resume, and stream operations.

Dependencies and integration points: depends on Linux common clock framework, runtime PM, platform device state, and MFC variant data. Operation backends call `s5p_mfc_clock_on/off` around firmware work; probe/remove and system PM paths call power helpers.

Risks: `s5p_mfc_clock_on/off` call `clk_enable/disable` on `clock_gate`; if `use_clock_gating` is false and `clock_gate` remains NULL, callers must not use these helpers or clock APIs must tolerate the pointer. Optional-clock handling only ignores `-ENOENT` for nonzero clock indexes. Failure rollback in `power_on` assumes only clocks before index `i` were enabled.

Test signals: probe/remove with variants having one clock, multiple clocks, and optional missing clocks; runtime suspend/resume; stream start/stop clock balance; failure injection for `clk_prepare_enable`; and lockdep/PM-runtime warnings under concurrent contexts.
