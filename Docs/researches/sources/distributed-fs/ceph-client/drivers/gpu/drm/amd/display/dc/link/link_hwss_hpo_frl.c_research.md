# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_hwss_hpo_frl.c

## Purpose

`link_hwss_hpo_frl.c` implements the HWSS vtable for HPO FRL, the HDMI FRL high-performance output path. It reuses virtual no-op stream encoder setup/reset and supplies HDMI FRL stream attribute programming.

## Important APIs, Types, And Functions

- `setup_hpo_frl_stream_attribute()` counts ODM combine segments by walking `pipe_ctx->next_odm_pipe`, then calls `hdmi_frl_set_stream_attribute()` with stream timing, FRL borrow parameters, and ODM segment count.
- `can_use_hpo_frl_link_hwss()` checks for `link_res->hpo_frl_link_enc`.
- `get_hpo_frl_link_hwss()` returns the static HPO FRL vtable.

## Control Flow

The vtable maps setup/reset stream encoder to virtual no-ops and maps stream attribute setup to FRL-specific programming. There is no link output enable/disable function in this vtable; other hardware sequencing layers handle the link output path.

## State And Persistence Behavior

The implementation mutates HPO FRL stream encoder attribute registers through function pointers. It reads `stream->link->frl_link_settings.borrow_params` and pipe ODM topology but stores no private state.

## Dependencies And Integration Points

It includes `link_hwss_hpo_frl.h`, `core_types.h`, and `virtual/virtual_link_hwss.h`. It integrates with HDMI FRL stream setup for ODM-combined modes.

## Risks And Edge Cases

The ODM segment count depends on a correct `next_odm_pipe` chain. Missing `hpo_frl_stream_enc` or malformed FRL link settings would fail through function-pointer use. The vtable is sparse, so callers must not expect DP-style payload/audio/test-pattern operations here.

## Test Signals

Exercise HDMI FRL modes with and without ODM combine, verify stream attributes and borrow parameters, and validate HWSS selection only when an HPO FRL link encoder resource exists.
