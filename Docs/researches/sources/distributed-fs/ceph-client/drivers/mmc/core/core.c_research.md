# sources/distributed-fs/ceph-client/drivers/mmc/core/core.c

## Purpose
Core MMC/SD/SDIO implementation for request execution, host claiming, power/voltage/timing control, erase/discard helpers, detection/rescan, card removal checks, CQE recovery, and subsystem init/exit.

## Important APIs, Types, And Functions
- Request APIs: `mmc_start_request()`, `mmc_request_done()`, `mmc_wait_for_req()`, `mmc_wait_for_cmd()`, `mmc_cqe_start_req()`, `mmc_cqe_request_done()`, `mmc_cqe_recovery()`.
- Host ownership: `__mmc_claim_host()`, `mmc_release_host()`, `mmc_get_card()`, `mmc_put_card()`.
- Power/bus: `mmc_attach_bus()`, `mmc_power_up()`, `mmc_power_off()`, `mmc_power_cycle()`, `mmc_set_initial_state()`.
- Erase/detection: `mmc_erase()`, `mmc_calc_max_discard()`, `mmc_detect_change()`, `mmc_rescan()`, `mmc_start_host()`, `mmc_stop_host()`.

## Control Flow
Callers claim a host, prepare requests, and submit through core helpers. The core validates request geometry, performs retuning, traces start/done, delegates transfer to host or CQE ops, handles retries/fault injection/LEDs, and invokes completion callbacks. Rescan powers the bus, tries UHS-II, then SDIO, SD, and MMC attachment at initialization frequencies. Stop cancels detection, removes bus/card state, detaches bus ops, and powers off.

## State And Persistence
State lives in `mmc_host` fields: claim counts, IOS, retune flags/timer, ongoing request, detect work, bus ops, card pointer, PM state, error stats, and pwrseq state. Card erase/discard geometry and removal flags are updated at runtime.

## Dependencies And Integration Points
Depends on host/CQE callbacks, pwrseq, GPIO card detect, regulator/undervoltage hooks, runtime PM, workqueues, completions, tracepoints, LEDs, fault injection, SD/SDIO/MMC helpers, and crypto reset hooks.

## Risks And Edge Cases
Claim/release imbalance can deadlock. Retuning must be held around sensitive operations and CQE recovery. Voltage switching can require power cycling. Erase timeout math must avoid overflow and respect host limits. Card removal races with in-flight requests and mechanical detect delays.

## Test Signals
Enumeration of SDIO/SD/MMC cards, request tracepoints, injected retry behavior, CQE recovery, suspend/resume/runtime PM stability, discard/trim correctness, voltage-switch fallback, and clean hotplug removal.
