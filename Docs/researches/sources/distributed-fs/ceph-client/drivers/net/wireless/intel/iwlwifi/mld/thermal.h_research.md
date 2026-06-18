# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.h

Purpose: Declares MLD thermal notification, threshold configuration, cTDP, and lifecycle APIs, with optional Linux thermal-framework state.

Important APIs and types: Under `CONFIG_THERMAL`, defines `struct iwl_mld_cooling_device` and declares `iwl_mld_config_ctdp()`. Always declares temp and CT-kill notification handlers, threshold configuration, thermal initialize, and thermal exit.

Control flow and integration: Included by MLD core setup and notification dispatch so thermal support can be compiled both with and without Linux thermal framework support.

State and persistence: Cooling-device state tracks current cooling state and registered thermal cooling device pointer when enabled.

Dependencies: Includes `iwl-trans.h`, optional `<linux/thermal.h>`, and forward declares `struct iwl_mld`.

Risks: Callers behind `CONFIG_THERMAL` must guard `iwl_mld_config_ctdp()` usage. Non-thermal builds still need CT-kill and firmware threshold handling.

Test signals: Build matrix coverage with `CONFIG_THERMAL=y` and disabled, plus notification dispatch compile coverage.
