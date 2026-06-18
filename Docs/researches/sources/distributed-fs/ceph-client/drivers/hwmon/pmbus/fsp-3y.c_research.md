# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/fsp-3y.c

Purpose: PMBus driver for FSP/3Y-Power YM-2151E and YH-5151E hot-swap power supplies. It handles nonstandard page numbering, required page-settle delays, and YH-5151E VOUT format variation.

Important APIs/types/functions: `struct fsp3y_data` embeds per-device PMBus info, detected chip ID, current real page, and `vout_linear_11` flag. `page_log_to_page_real()` maps logical PMBus pages to device-specific real page values. `set_page()` writes `PMBUS_PAGE` and waits 20-30 ms after changes. `fsp3y_read_byte_data()` fakes `VOUT_MODE` when needed. `fsp3y_read_word_data()` whitelists supported reads and performs linear11 VOUT conversion. `fsp3y_detect()` reads `PMBUS_MFR_MODEL`.

Control flow: probe allocates private data, detects the actual model, warns if configured I2C ID disagrees, reads current page, copies the static descriptor for that model, detects YH-5151E VOUT mode behavior, and calls PMBus core. All byte/word reads call `set_page()` first, translating PMBus logical pages to hardware pages and delaying after page changes.

State and persistence: state includes current real page and VOUT encoding mode in `fsp3y_data`. Hardware page selection changes during reads. Sensor values are not cached by this driver.

Dependencies and integration: depends on PMBus core, I2C SMBus byte/word/block operations, sleep/delay helpers, and direct model IDs. It imports namespace `PMBUS`.

Risks: page changes are timing-sensitive; reducing the delay can return wrong-page data. The whitelist excludes untested commands even if the device responds. VOUT format is detected per device by `VOUT_MODE == 0xff`; if firmware changes that indicator, scaling may break. Probe requires model block reads.

Test signals: model detection for both supported PSUs, logical-to-real page mapping, page delay behavior under repeated reads, YH-5151E linear11 fallback, unsupported command rejection, and visible attributes per page.
