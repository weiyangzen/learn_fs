# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.c

## Purpose

This file orchestrates the GuC, HuC, and GSC uC stack for a GT. It expands `enable_guc` defaults, confirms supported/wanted options, fetches and cleans firmware, initializes software objects, programs WOPCM, loads firmware in the required order, enables GuC communication/submission/SLPC, and handles reset, suspend, runtime suspend, resume, and teardown.

## Important APIs And Functions

Public functions include early/late init, driver remove/late release, MMIO init, reset prepare/reset/finish, cancel requests, suspend/runtime suspend, resume/runtime resume. The static `intel_uc_ops` tables select either off-mode checks/fini or full GuC-on behavior. `__uc_init_hw()` is the central hardware bring-up function: print firmware versions, validate loadability, program WOPCM, reset GuC, upload HuC, reset ADS, write GuC params, upload GuC, enable CT communication, authenticate/update HuC, enable GuC submission, and enable SLPC or lower RPS.

## Control Flow

`uc_expand_default_options()` enables nothing before Gen12, disables older Gen12 defaults, enables HuC-only on pre-RaptorLake ADL-S, and otherwise defaults to HuC plus GuC submission. Firmware fetch is GuC-first; GuC fetch failure forces HuC/GSC firmware status out of transient selected state. Hardware init retries GuC firmware upload three times on Gen9 workarounds and once elsewhere while temporarily disabling low PL1 power limits and raising unslice frequency.

Communication uses CT enable/disable plus scratch-register capture for messages that arrive while CT is disabled. Runtime suspend waits briefly for outstanding submission G2H replies, then disables communication. Full suspend flushes GSC work, wakes TLB invalidation waiters, flushes GuC submission work, and sends GuC suspend under runtime PM. Runtime resume reenables CT communication and ARAT interrupt masking when needed, resumes GuC/GSC, and invalidates engine and GuC TLBs if available.

## State, Dependencies, Risks, And Test Signals

Persistent state includes `uc->ops`, embedded `guc/huc/gsc`, `load_err_log`, `reset_in_progress`, `fw_table_invalid`, and GuC `mmio_msg`. Dependencies span GT reset, uncore MMIO, GuC CT, GuC ADS/SLPC/submission, HuC auth, GSC firmware, RPS/HWMON, runtime PM, WOPCM partitioning, and scratch registers. Risks include unsafe fallback after WOPCM has been locked, missed MMIO messages around CT transitions, HuC upload/auth failures being tolerated differently than GuC failures, reset nesting, and suspend races with outstanding CTB/G2H. Test signals are GuC/HuC firmware boot logs, WOPCM register programming, GuC load retries, captured GuC error log on failure, suspend/resume and runtime PM, GuC submission enablement, SLPC enablement, and TLB invalidation after resume.
