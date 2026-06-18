# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cqhci.h

## Purpose

`sdhci-cqhci.h` is a small shared helper for drivers that combine the SDHCI core with CQHCI command queue support. Its role is to coordinate full SDHCI resets with command-queue deactivation without making the SDHCI and CQHCI modules directly depend on each other in every driver.

## Important APIs, Types, And Functions

- Includes `cqhci.h` and `sdhci.h`, making CQHCI and SDHCI types visible to users.
- `sdhci_and_cqhci_reset(struct sdhci_host *host, u8 mask)` calls `cqhci_deactivate(host->mmc)` before `sdhci_reset(host, mask)` when CQE is enabled, the reset is `SDHCI_RESET_ALL`, and CQHCI private data exists.

## Control Flow

The helper is intended to be used as an SDHCI `.reset` operation or from platform reset callbacks. Partial command/data resets skip CQHCI deactivation; full resets deactivate CQHCI first, then perform the normal SDHCI reset.

## State And Persistence Behavior

The helper owns no state. It observes `mmc->caps2` and `mmc->cqe_private` and changes CQHCI runtime state by calling `cqhci_deactivate()`.

## Dependencies And Integration Points

Users include platform drivers such as Broadcom STB and i.MX eSDHC that support CQHCI. The helper integrates SDHCI reset semantics with CQHCI lifecycle expectations and relies on the MMC host capability bit as the guard.

## Risks And Edge Cases

- Drivers must use this helper on full resets when CQE is enabled; using raw `sdhci_reset()` can leave CQHCI state active across a controller reset.
- The helper only deactivates on `SDHCI_RESET_ALL`; controller-specific command/data resets may need additional handling.
- Incorrectly set `MMC_CAP2_CQE` or `cqe_private` can either skip required deactivation or call CQHCI when not fully initialized.

## Test Signals

Relevant tests are CQE-enabled I/O followed by full controller reset, suspend/resume with CQHCI, recovery from command/data errors, and driver-specific reset paths verifying `cqhci_deactivate()` precedes SDHCI reset.
