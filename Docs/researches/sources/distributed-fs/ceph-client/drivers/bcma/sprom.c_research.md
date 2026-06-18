# sources/distributed-fs/ceph-client/drivers/bcma/sprom.c

Purpose: locates, validates, and extracts BCMA SPROM data into `bus->sprom`. It supports external SPROM, on-chip OTP-backed SPROM, and architecture-provided fallback SPROM, then decodes revision 8-11 Broadcom calibration, board, GPIO, antenna, and power fields.

Important APIs and functions: `bcma_arch_register_fallback_sprom()` registers a platform callback. `bcma_sprom_get()` is the top-level retrieval API used by bus registration. `bcma_sprom_read()` reads 16-bit words from chipcommon SPROM space. `bcma_sprom_crc()`, `bcma_sprom_check_crc()`, and `bcma_sprom_valid()` validate CRC and supported revisions. `bcma_sprom_extract_r8()` performs the large field extraction using `SPEX`, `SPEX32`, and `SPEX_ARRAY8` macros. Availability helpers check external SPROM presence, on-chip OTP presence, and OTP offset.

Control flow: `bcma_sprom_get()` first requires a chipcommon core. It prefers external SPROM; when absent, it checks on-chip OTP and computes an offset; if neither is usable it calls the fallback callback. It temporarily disables external PA lines on BCM4331/43431, tries several SPROM word sizes, validates CRC/revision, restores PA lines, then either extracts fields or falls back after invalid reads.

State and persistence: decoded values persist in `bus->sprom`, including revision, board flags, MAC address, country code, per-core power info, FEM, antenna gain, PA curves, MCS/OFDM power offsets, temperature calibration, GPIOs, chains, and board metadata. `get_fallback_sprom` is a single global callback pointer.

Dependencies and integration points: depends on chipcommon registers/capabilities, SSB SPROM layout constants, BCMA chip IDs, PCI/SoC bus registration, and platform architecture callbacks. `main.c` calls this after early core setup and early flash-capable core registration.

Risks: only revisions 8-11 are accepted, so older/newer SPROM layouts require code changes. Fallback callback is global and only one can be registered. CRC or offset failures can silently move to fallback, masking bad hardware reads. Extraction is macro-heavy and easy to mis-map. Test signals include valid CRC on known SPROM dumps, fallback path for SPROM-less SoCs, OTP offset handling, BCM4331 PA-line toggling, and decoded regulatory/power fields matching hardware expectations.
