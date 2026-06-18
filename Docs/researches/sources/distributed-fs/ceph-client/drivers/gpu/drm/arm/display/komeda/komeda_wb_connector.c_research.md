# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_wb_connector.c

## Purpose

`komeda_wb_connector.c` implements Komeda DRM writeback connector support. It exposes a virtual always-connected writeback connector per CRTC when the master pipeline has a writeback layer, advertises formats supported by that writeback layer, and validates/builds Komeda data-flow state for capturing the composition output into a framebuffer.

## Important APIs, Types, And Functions

The exported API is `komeda_kms_add_wb_connectors()`, which iterates all Komeda CRTCs and calls the internal `komeda_wb_connector_add()`. The connector uses `drm_writeback_connector_init()` with `komeda_wb_connector_funcs` and `komeda_wb_encoder_helper_funcs`. The important validation path is `komeda_wb_encoder_atomic_check()`, which checks for an active CRTC, fetches the target `struct drm_writeback_job`, initializes a `struct komeda_data_flow_cfg` via `komeda_wb_init_data_flow()`, and routes either through `komeda_build_wb_data_flow()` or `komeda_build_wb_split_data_flow()`.

## Control Flow

During KMS initialization, each CRTC with `kcrtc->master->wb_layer` gets a `struct komeda_wb_connector`. Initialization allocates the wrapper, stores the writeback layer, obtains a FourCC list from the format table for that layer type, registers the writeback connector with a possible-CRTC mask for the owning CRTC, attaches connector helpers, and fills display-info color depth/format capabilities from the pipeline improc block. During an atomic commit check, no writeback job means no work. A job on an inactive CRTC fails. A job on an active CRTC builds a data-flow description where the input comes from the pipeline compiz output and the output dimensions come from the writeback framebuffer.

## State And Persistence Behavior

Persistent driver state is limited to the allocated `struct komeda_wb_connector`, its `wb_layer` pointer, and `kcrtc->wb_conn`. Per-commit data-flow state is temporary and lives in atomic state objects. The connector is always reported connected, has no modes of its own, and accepts modes only within `drm_mode_config` min/max dimensions. Destroy cleans up the DRM connector and frees the wrapper.

## Dependencies And Integration Points

This file integrates Komeda KMS objects, Komeda pipeline composition helpers, layer format-table helpers, DRM writeback core, DRM atomic connector/encoder helpers, and Komeda data-flow builders. It depends on the surrounding Komeda pipeline model: compiz is the source for captured frames, the writeback layer is the sink, and split writeback is delegated to Komeda data-flow construction.

## Risks And Edge Cases

The atomic check mutates `crtc_st->connectors_changed` when the only connector change is the writeback connector; mistakes here can trigger unnecessary modesets or skip required ones. The code assumes `conn_st->writeback_job->fb` is valid when `writeback_job` is non-NULL. Format-list allocation and connector registration failures must free the wrapper and return promptly. Split data-flow handling is selected from `dflow.en_split`, so correctness depends on `komeda_complete_data_flow_cfg()`.

## Test Signals

Useful signals include Komeda probe with pipelines that both have and lack a writeback layer, writeback jobs for every advertised writeback format, inactive-CRTC writeback rejection, writeback-only atomic commits that do not force a modeset, split and non-split writeback coverage, connector cleanup on bind failure/unbind, and IGT writeback tests validating captured frame dimensions and contents.
