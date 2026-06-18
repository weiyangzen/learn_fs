# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.h

Purpose: declares MFC runtime PM, power, and clock helper functions.

Important APIs and types: exports `s5p_mfc_init_pm`, `s5p_mfc_final_pm`, `s5p_mfc_clock_on`, `s5p_mfc_clock_off`, `s5p_mfc_power_on`, and `s5p_mfc_power_off`, all operating on `struct s5p_mfc_dev`.

Control flow: device probe initializes PM, runtime stream/scheduler paths gate clocks, and remove or failure paths finalize PM and power down resources.

State and persistence: no state is held in the header. Declared functions mutate `dev->pm`, runtime PM usage count, and clock prepare/enable state.

Dependencies and integration points: requires consumer visibility of `struct s5p_mfc_dev`. It is included by operation backends and core device setup code.

Risks: the API separates whole-device power from software clock gating, so callers must pair the correct helper families. Misbalanced calls can leave firmware inaccessible or clocks enabled.

Test signals: compile coverage; runtime PM balance checks; stream start/stop cycles; and suspend/resume tests.
