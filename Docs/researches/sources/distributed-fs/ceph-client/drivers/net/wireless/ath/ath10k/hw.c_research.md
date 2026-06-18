# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.c

## Purpose

`hw.c` supplies target-specific hardware tables and hardware operations for ath10k. It defines register base maps, Copy Engine register layouts, common per-chip values, QCA6174 clock parameters, survey counter conversion, coverage-class register programming, QCA6174 PLL bring-up, segmented firmware download through diagnostic access, and small operation hooks for HTT TX completion RSSI parsing.

## Important APIs, Types, and Functions

- Exported tables: `qca988x_regs`, `qca6174_regs`, `qca99x0_regs`, `qca4019_regs`, `wcn3990_regs`, `qca988x_values`, `qca6174_values`, `qca99x0_values`, `qca9888_values`, `qca4019_values`, `wcn3990_values`, `qcax_ce_regs`, `wcn3990_ce_regs`, `qca6174_clk`.
- Public functions: `ath10k_hw_fill_survey_time()` and `ath10k_hw_diag_fast_download()`.
- Hardware ops tables: `qca988x_ops`, `qca99x0_ops`, `qca6174_ops`, `qca6174_sdio_ops`, `wcn3990_ops`.
- Internal operations: `ath10k_hw_qca988x_set_coverage_class()`, `ath10k_hw_qca6174_enable_pll_clock()`, `ath10k_hw_map_target_mem()`, `ath10k_hw_diag_segment_msb_download()`, `ath10k_hw_diag_segment_download()`.

## Control Flow

Most of the file is static data consumed during device matching and bus setup. Register maps provide per-chip base addresses and interrupt masks. Value tables provide CE counts, MSI assignment limits, descriptor metadata masks, RTC state constants, and optional RFKill GPIO defaults. CE register structures describe how HIF code should program source/destination rings, watermarks, misc error interrupts, host interrupt enable bits, and command halt fields for qcax-style targets and WCN3990.

`ath10k_hw_fill_survey_time()` receives current and previous cycle counters, compensates for chip-specific wraparound behavior, marks survey time fields, and converts counts to milliseconds using `CCNT_TO_MSEC()`. For the shifted-all wraparound type, a wrap in the primary cycle counter suppresses busy-time reporting because relative busy time cannot be trusted.

`ath10k_hw_qca988x_set_coverage_class()` runs under `conf_mutex`, stores the requested coverage class if firmware is not started, otherwise reads MAC slot/ACK/CTS/PHY clock registers, verifies expected slot-time units, recalculates propagation-delay-adjusted register values, writes them through HIF, and raises firmware debug logging to WARN level when coverage class is nonzero so firmware resets can be noticed and corrected.

`ath10k_hw_qca6174_enable_pll_clock()` is a strict BMI register/memory sequence. It validates clock register addresses, reads efuse-selected reference clock index, programs PLL fraction/outdiv/settle/div/refdiv/nopwd/bypass bits, busy-waits for RTC sync twice, enables standard CPU clock, powers down PLL control bits as required, writes target clock init memory, and finally writes the target CPU frequency.

`ath10k_hw_diag_fast_download()` parses a segmented BMI firmware image. It validates magic and flags, iterates metadata records, sets start addresses, rejects unsupported BDDATA/EXEC markers, checks segment sizes, and writes each segment either directly through `ath10k_hif_diag_write()` or through `ath10k_hw_diag_segment_msb_download()` when a target address crosses the 1 MiB diagnostic window. The MSB mapper is reset to DRAM after special-region writes.

RSSI helper ops inspect HTT TX completion flags. WCN3990 uses different RSSI enable and padding bits, so it has a separate `wcn3990_ops` table.

## State and Persistence Behavior

The exported tables are immutable compile-time configuration. Runtime mutations are limited to `ar->fw_coverage` cache fields, survey output fields, firmware debug log settings, HIF/BMI target registers, and diagnostic memory writes. PLL and diag download operations affect target hardware/firmware boot state but do not persist on the host filesystem.

## Dependencies and Integration Points

This file depends on `core.h`, `hw.h`, HIF register access, WMI debug-log ops, BMI register/memory access, firmware segmented image definitions, and RX descriptor abstractions. Its data is consumed by bus drivers, CE setup, firmware download, reset/boot code, survey reporting, HTT TX completion parsing, and mac80211 coverage class handling through `hw_ops`.

## Risks

- Hardware tables are trusted constants. An incorrect base address, mask, CE count, or interrupt bit silently misprograms the device.
- Coverage-class programming bypasses firmware and assumes wave1 register layout and slot-time values; unexpected firmware register changes are only partially guarded.
- PLL bring-up uses a sensitive ordered sequence and busy-wait timeout. Refactoring or changing masks can produce boot failures that are hard to diagnose.
- Diagnostic fast download must split across 1 MiB windows correctly and restore the CPU address MSB. Truncated or malformed segmented images are rejected, but target writes are irreversible within a boot attempt.
- RSSI completion padding depends on firmware flags matching the completion layout used by `htt_rx.c`.

## Test Signals

Important tests include per-chip register/value table selection, CE setup register programming for qcax and WCN3990 layouts, survey time wraparound cases for all three wrap modes, coverage class when device is off vs on/restarted, invalid slot/phy clock register reads, QCA6174 PLL efuse index bounds and busy-wait timeout paths, segmented firmware images with begin/done/unsupported/truncated/oversized/cross-window records, and HTT TX RSSI flag/padding interpretation for WCN3990 vs non-WCN3990. Runtime signals include boot debug messages, coverage-class warnings, BMI/HIF write failures, survey time fields, and firmware download success/failure logs.
