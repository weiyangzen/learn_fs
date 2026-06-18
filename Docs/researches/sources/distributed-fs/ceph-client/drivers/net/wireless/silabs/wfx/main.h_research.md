# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.h

Purpose: Declares common WFx platform data and common probe/lifecycle helper APIs.

Important APIs and types: `struct wfx_platform_data` carries firmware base name, PDS file name, wakeup GPIO, and rising-clock preference. Exports `wfx_init_common()`, `wfx_probe()`, `wfx_release()`, `wfx_api_older_than()`, and `wfx_send_pds()`.

Control flow and integration: SPI/SDIO bus drivers supply platform data and bus ops to `wfx_init_common()`, then call `wfx_probe()`. `wfx_release()` is used during bus remove. API-version checks gate firmware compatibility in BH, data RX, station, and HIF paths. Debugfs can call `wfx_send_pds()` to upload PDS chunks.

State and persistence: Platform data persists inside `wdev->pdata`, including optional DT-overridden PDS file and wakeup GPIO.

Dependencies: Depends on Linux device/GPIO APIs, WFx HIF general startup definitions, and bus abstraction.

Risks and test signals: Tests should cover platform data copying, DT PDS override, optional wakeup GPIO handling, API comparison boundary cases, and PDS chunk validation.

Test signals: Source read size: 41 lines, 1148 bytes.
