# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.c

## Purpose
This file implements legacy ATOMBIOS DisplayPort support: AUX transfer through ATOM command tables, DPCD discovery, DP link configuration selection, panel mode detection, sink power control, link-training state machine, and encoder-service queries.

## Important APIs, types, and functions
`amdgpu_atombios_dp_aux_init()` initializes the DRM DP AUX adapter around the AMDGPU DDC bus and ATOM AUX transfer callback. `amdgpu_atombios_dp_process_aux_ch()` executes `ProcessAuxChannelTransaction` using the ATOM scratch area and returns reply status/data. `amdgpu_atombios_dp_aux_transfer()` translates DRM AUX messages into the ATOM packet format.

Discovery/config helpers include `amdgpu_atombios_dp_get_sinktype()`, `amdgpu_atombios_dp_probe_oui()`, `amdgpu_atombios_dp_ds_ports()`, `amdgpu_atombios_dp_get_dpcd()`, `amdgpu_atombios_dp_get_panel_mode()`, `amdgpu_atombios_dp_set_link_config()`, `amdgpu_atombios_dp_mode_valid_helper()`, `amdgpu_atombios_dp_needs_link_train()`, and `amdgpu_atombios_dp_set_rx_power_state()`.

Link training uses `struct amdgpu_atombios_dp_link_train_info`, `amdgpu_atombios_dp_get_adjust_train()`, `amdgpu_atombios_dp_update_vs_emph()`, `amdgpu_atombios_dp_set_tp()`, `amdgpu_atombios_dp_link_train_init()`, clock recovery `amdgpu_atombios_dp_link_train_cr()`, channel equalization `amdgpu_atombios_dp_link_train_ce()`, finish `amdgpu_atombios_dp_link_train_finish()`, and public `amdgpu_atombios_dp_link_train()`.

## Control flow
AUX init installs `amdgpu_atombios_dp_aux_transfer()` into the connector's DDC bus. Transfers build a four-byte DP AUX header, append payload for writes, call the ATOM AUX transaction table under the bus mutex, convert timeout/error reply statuses to Linux errors, copy received bytes from ATOM scratch, and set `msg->reply`.

DPCD discovery reads receiver caps, copies them into connector private state, probes OUI and downstream port data, or clears DPCD on failure. Link config chooses the lowest sufficient lane/rate pair from 1.62, 2.7, and 5.4 Gbit/s, with a Nutmeg bridge special case fixed at 2.7 Gbit/s. Link training powers the sink, enables downspread/eDP config, sets lane count and link rate, starts source training, performs clock recovery with max-voltage and repeated-voltage limits, performs channel equalization with TP2/TP3, then disables training patterns on both sink and source.

## State and persistence behavior
The file mutates connector private DP state: DPCD cache, downstream ports, sink type, lane count, DP clock, and panel mode. It mutates sink DPCD registers over AUX and source encoder/transmitter state through ATOM encoder helpers. AUX transactions use `atom_context->scratch` as transient shared storage. The DDC bus mutex serializes AUX command-table access.

## Dependencies
It depends on DRM DP helper functions, AMDGPU connector/encoder/DDC structures, ATOM interpreter and command tables, ATOMBIOS encoder helpers, and connector bpc/bridge helpers.

## Integration points
Connector detection reads DPCD and sink type through this file. Modeset validation uses `amdgpu_atombios_dp_mode_valid_helper()`. Modeset setup calls `set_link_config`, power state, and link training. CRTC PLL code uses the selected DP clock.

## Risks and edge cases
AUX transfers are limited to 16-byte payloads and depend on scratch memory layout at offsets 4 and 20. `amdgpu_atombios_dp_ds_ports()` clears downstream ports whenever `drm_dp_dpcd_read()` returns any nonzero value, which appears inverted relative to the usual positive-byte-count success convention and deserves review. Link config ignores 8b/10b overhead beyond the simple `* 8 / bpp` formula and has fixed rates. Link training returns only through logs; final failure does not propagate to callers. Some paths assume connector private data and DDC bus are present. Training loop limits and delays must track DP spec evolution.

## Test signals
Tests should cover AUX native/I2C read/write formatting, reply-status error mapping, DPCD read failure handling, OUI/downstream-port handling, bridge-specific link selection, DP1.2 5.4 Gbit/s validation, eDP panel mode detection, link-training success and max-voltage/retry failures, and sink power state writes.
