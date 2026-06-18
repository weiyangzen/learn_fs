# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_timings.c

Purpose: this file is the raw NAND timing database and conversion helper for ONFI SDR and NVDDR interface modes. It provides reset defaults, closest-mode matching, and interface-config filling with dynamic timing values from the detected ONFI parameter page.

Important APIs, types, and functions: `nand_get_reset_interface_config()`, `onfi_find_closest_sdr_mode()`, `onfi_find_closest_nvddr_mode()`, and `onfi_fill_interface_config()` are the exported helpers. Static arrays `onfi_sdr_timings[]` and `onfi_nvddr_timings[]` define modes 0-5 in picoseconds.

Control flow: callers request a reset config, find the fastest ONFI mode satisfying a timing structure, or fill a config for a specific SDR/NVDDR mode. Fill helpers copy the static table entry and then override dynamic values such as tPROG, tBERS, tR, tCCS, and NVDDR tCAD from `chip->parameters.onfi` when available.

State and persistence: timing tables are immutable. Filled `struct nand_interface_config` values are caller-owned and transient. The only input state is `chip->parameters.onfi`.

Dependencies and integration points: this code integrates with detection results from `nand_onfi.c`, manufacturer timing quirks, controller `setup_interface` support, and core timing negotiation routines.

Risks: closest-mode helpers compare only minimum constraints, so callers must handle max timing and controller-side limits separately. Non-ONFI chips use intentionally conservative dynamic maxima. Invalid timing-mode indexes only warn and leave the caller's config unchanged.

Test signals: validate mode table values, closest-mode selection for SDR and NVDDR boundary timings, ONFI dynamic tPROG/tBERS/tR/tCCS override behavior, fast-tCAD behavior, reset mode 0 selection, and invalid mode handling.
