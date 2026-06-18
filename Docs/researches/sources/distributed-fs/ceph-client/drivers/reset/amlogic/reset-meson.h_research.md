# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.h

Purpose: shared header contract for Amlogic Meson reset platform and auxiliary drivers.

Important APIs/types/functions: defines `struct meson_reset_param` with reset ops, reset count, reset/level offsets, and active-low flag; declares `meson_reset_controller_register()`, `meson_reset_ops`, and `meson_reset_toggle_ops`.

Control flow: no runtime flow, but callers pass parameter tables to common registration to choose pulse or toggle semantics and layout offsets.

State and persistence: no state in the header; it defines how runtime state is configured by source files.

Dependencies and integration: includes module, regmap, and reset-controller headers. It is the compile-time boundary between `reset-meson-common.c`, `reset-meson.c`, and `reset-meson-aux.c`.

Risks and test signals: field interpretation changes affect every Meson reset provider. Signals are successful builds for all Meson objects and runtime confirmation that platform/auxiliary callers choose the right exported ops.
