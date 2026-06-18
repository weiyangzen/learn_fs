# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinctrl-state.h

Purpose: centralizes the standard pinctrl state names used by consumers, hogs, and power-management code.

Important APIs and types: defines `PINCTRL_STATE_DEFAULT`, `PINCTRL_STATE_INIT`, `PINCTRL_STATE_IDLE`, and `PINCTRL_STATE_SLEEP` as the canonical string names `"default"`, `"init"`, `"idle"`, and `"sleep"`.

Control flow: device core and drivers request/select these named states through the pinctrl consumer API. `init` can be applied before probe to avoid glitches, then transitioned to `default`; `idle` is commonly selected for runtime suspend/idle; `sleep` is selected for system suspend.

State and persistence: no state is stored here. The names map to firmware-described pinctrl state objects, and hardware persistence depends on the controller and PM path.

Dependencies and integration points: it is a dependency-light naming contract between board firmware, device drivers, pinctrl core, runtime PM, system suspend/resume, and pin hog setup.

Risks and test signals: risks are naming drift in firmware, missing states causing fallback behavior, and incorrect `init`/`default` sequencing that can glitch external signals. Test by booting with hog states, probing devices with `init`, runtime suspend/resume selecting `idle`, and system suspend/resume selecting `sleep`/`default`.
