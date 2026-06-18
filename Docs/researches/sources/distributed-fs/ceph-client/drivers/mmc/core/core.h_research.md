# sources/distributed-fs/ceph-client/drivers/mmc/core/core.h

## Purpose
Private MMC core API shared by protocol, bus, block, host, and helper files.

## Important APIs, Types, And Functions
- `struct mmc_bus_ops` defines active bus callbacks for remove, detect, PM, alive, reset, cache, and undervoltage behavior.
- Declares power, voltage, timing, request, erase, claim, detection, bus attach, and card attach helpers.
- Inline wrappers include `mmc_delay()`, `mmc_claim_host()`, `mmc_pre_req()`, `mmc_post_req()`, `mmc_cache_enabled()`, `mmc_flush_cache()`, and sector math.

## Control Flow
Implementation files include this header to call core helpers and attach protocol-specific bus operations to a host.

## State And Persistence
No header-owned state. Functions mutate `mmc_host`, `mmc_card`, and `mmc_request` state.

## Dependencies And Integration Points
Depends on delay/scheduler primitives and public MMC structures; central private contract for core, protocol, block, bus, host, debugfs, and pwrseq code.

## Risks And Edge Cases
Signature changes have broad blast radius. Inline wrappers assume valid `host->ops` and `host->bus_ops` in the lifecycle phase where they are called.

## Test Signals
Compile all MMC configs; runtime card attach, request submission, erase/discard, debugfs stubs, and suspend/resume.
