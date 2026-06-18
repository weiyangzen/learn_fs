# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/interface/ia_css_ifmtr.h

Purpose: exposes host-side input-formatter configuration helpers.

Important APIs/state: `ia_css_ifmtr_lines_needed_for_bayer_order`, `ia_css_ifmtr_columns_needed_for_bayer_order`, and `ia_css_ifmtr_configure`. The header also exposes `ifmtr_set_if_blocking_mode_reset`, a global reset guard controlling whether formatter blocking mode is programmed.

Control flow: callers provide a stream config and optional binary. The implementation computes crop starts, formatter buffer layout, and pushes configs into SP state when a physical input formatter is needed.

Dependencies/integration: depends on stream public config and binary descriptors; implementation calls input formatter hardware APIs and `sh_css_sp_set_if_configs`.

Risks: exposing the reset flag allows external code to affect global hardware reset behavior. Configuration is sensitive to input format, two-pixels-per-clock, bayer order, continuous/copy mode, and left padding.

Test signals: bayer-order line/column correction, memory input mode no-op config index, sensor-port config selection, and reset flag behavior across consecutive streams.
