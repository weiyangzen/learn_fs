# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.h

Purpose: Firmware and SDD constants plus the firmware loading interface.

Important APIs and types: Defines firmware blob names (`wsm_10.bin`, `wsm_11.bin`, `wsm_20.bin`, `wsm_22.bin`, `wsm_cw1x60.bin`), SDD blob names, SDD TLV element IDs for PTA config and reference frequency, declares `cw1200_load_firmware`, and declares `cw1200_dpll_from_clk`.

Control flow: Used by firmware loading to select files by hardware revision and by MAC setup to parse SDD TLVs.

State and persistence: No direct state; file names correspond to firmware files persisted in the system firmware search path.

Dependencies and integration: Tied to `fwio.c`, `sta.c` SDD parsing, and platform/module overrides for `sdd_path`.

Risks: File names are ABI-like expectations for distributions and firmware packages. Missing or mismatched SDD files can break calibration/reference-clock behavior.

Test signals: Firmware package validation should include all named blobs needed by supported hardware; SDD parsing should confirm reference clock and PTA listen interval.
