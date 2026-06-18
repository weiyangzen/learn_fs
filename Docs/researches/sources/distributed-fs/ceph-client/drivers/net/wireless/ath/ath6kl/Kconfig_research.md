# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Kconfig

Purpose: Defines Kconfig options for the ath6kl core, SDIO bus driver, USB bus driver, debug support, event tracing, and optional regulatory-domain firmware control.

Important symbols: `ATH6KL` is the core tristate and depends on `CFG80211`. `ATH6KL_SDIO` depends on `ATH6KL` and `MMC`. `ATH6KL_USB` depends on `ATH6KL` and `USB`. `ATH6KL_DEBUG` enables debug messages/debugfs. `ATH6KL_TRACING` depends on `EVENT_TRACING`. `ATH6KL_REGDOMAIN` depends on `CFG80211_CERTIFICATION_ONUS` and allows firmware regdomain changes.

Control flow: Kconfig dependency selection determines which modules are built and which optional code paths are compiled. The core can be built without a bus driver, but real hardware requires SDIO or USB. Debug, tracing, and regulatory paths gate code in other ath6kl files.

State and persistence: No runtime state. The selected configuration persists in the kernel build configuration and module set.

Dependencies and integration points: Integrates with the kernel wireless menu, cfg80211, MMC, USB, event tracing, debugfs/debug message code, and regulatory certification policy. Module names advertised in help text align with Makefile outputs `ath6kl_core`, `ath6kl_sdio`, and `ath6kl_usb`.

Risks: Enabling `ATH6KL_REGDOMAIN` carries explicit regulatory responsibility. Building core without a transport driver produces no usable device support. Debug/tracing options increase diagnostic surface and may add overhead or expose sensitive packet/control data when enabled.

Test signals: Compile matrix for built-in/module combinations of core, SDIO, USB, debug, tracing, and regdomain; verify dependency enforcement; modprobe expected module names; and confirm unsupported AR6001/AR6002 expectations remain documented.
