# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.c

Purpose: this file implements the DCN 3.2 DCCG variant. It is structurally close to DCN 3.1.4 but chooses DCN 2 DPP DTO behavior, adds a guarded DIO FIFO resync, treats HDMI idle pixel DTO source specially, and always sources DTBCLK_P from DTBCLK0 for DP stream clock setup.

Important APIs and functions: `dccg32_create()` installs `dccg32_funcs`. Local helpers cover DIO FIFO resync, K1/K2 pixel-rate divider read/write, DTBCLK_P source selection, DTBCLK DTO programming, valid pixel rate setup, DCCG reference frequency, DP stream clock routing, and OTG add/drop pixel writes. The callback table uses `dccg2_update_dpp_dto`, `dccg31_init`, `dccg31_*` HPO/PHY/audio helpers, and `dccg2_*` compatibility callbacks.

Control flow: `dccg32_trigger_dio_fifo_resync()` reads `DENTIST_DISPCLK_RDIVIDER` and writes it to `WDIVIDER` only when nonzero. DTB DTO enable mirrors DCN 3.1.4: program quarter pixel rate, enable DTO, wait for status, set K1/K2 to 1:1, then set pipe DTO source `2`. Disable clears modulo/phase and selects source `0` for HDMI or `1` otherwise. `dccg32_set_valid_pixel_rate()` sets `is_hdmi = true` to select the HDMI-specific idle source. `dccg32_set_dpstreamclk()` always calls `dccg32_set_dtbclk_p_src(dccg, DTBCLK0, otg_inst)` before toggling a DP stream clock, independent of the requested `src` except for enable state.

State and persistence: mutable state is limited to hardware registers and inherited `struct dccg` fields. The code updates no persistent storage.

Dependencies and integration: it depends on `dcn32_dccg.h`, `dcn20_dccg.h`, and DCN 3.1 helpers declared by `dcn32_dccg.h`. It integrates by returning a `struct dccg` with a local function table assembled from DCN 3.2 and inherited callbacks.

Risks: always programming DTBCLK_P to DTBCLK0 in `set_dpstreamclk` means callers cannot use DPREFCLK there despite the lower helper supporting it. The quarter-rate DTO assumption is inherited from DCN 3.1.4. Invalid OTG/HPO instances only debug-break and return. `get_dccg_ref_freq()` comments expect 100 MHz but still returns `xtalin_freq_inKhz`, so callers must supply the correct board value.

Test signals: validate FIFO resync skips zero RDIVIDER, HDMI versus non-HDMI DTO-source selection on disable, DP stream clock routing for all HPO instances, K1/K2 divider programming, inherited HPO/PHY/DSC behavior on DCN 3.2 tables, and DPP DTO behavior through the older `dccg2_update_dpp_dto` callback.
