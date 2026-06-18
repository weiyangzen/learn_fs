# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.c

## Purpose

`cc_pm.c` implements runtime power management for the ccree CryptoCell device. It powers the hardware down when idle, restores clocks and registers on resume, and exposes small wrappers used by request submission to hold runtime PM references while hardware descriptors are outstanding.

## Important APIs, Types, And Functions

`cc_pm_suspend()` finalizes CryptoCell registers, enables `HOST_POWER_DOWN_EN`, and disables the device clock. `cc_pm_resume()` enables the clock, waits for reset completion, disables power-down, reinitializes common registers, handles TEE/FIPS errors, and reinitializes hash SRAM constants. `ccree_pm` exports runtime PM ops. `cc_pm_get()` wraps `pm_runtime_get_sync()` and unwinds failed gets; `cc_pm_put_suspend()` calls `pm_runtime_put_autosuspend()`.

## Control Flow

Asynchronous and synchronous request submission call `cc_pm_get()` before queue admission. Completion processing calls `cc_pm_put_suspend()` after each dequeued request callback. Runtime suspend runs only when the PM core decides the device is idle. Resume must complete register and SRAM initialization before any queued descriptor sequence can rely on hardware state.

## State And Persistence Behavior

Runtime suspend intentionally drops volatile hardware state: clocks are disabled and the power-down bit is set. Resume restores register programming and hash SRAM constants, but per-request and per-transform DMA memory remains host-side. FIPS/TEE status may be detected after power-down and handled during resume.

## Dependencies And Integration Points

The file depends on Linux runtime PM, clocks, interrupt headers, ccree driver init/fini helpers, SRAM manager, hash SRAM initialization, and FIPS handling. It is included through `cc_pm.h` by the request manager, making PM lifetime management part of request submission semantics.

## Risks And Edge Cases

If resume cannot enable the clock or reset does not complete, future crypto requests fail. Forgetting to reinitialize hash SRAM after resume would break hash and AEAD operations using SRAM larval constants. PM reference imbalance in the request manager would either prevent autosuspend or suspend the device with descriptors still active.

## Test Signals

Enable runtime PM autosuspend and run crypto self-tests before and after idle suspend. Logs should not show reset timeout or `init_cc_regs` errors. Hash operations after resume validate SRAM reload. PM debug counters should show balanced gets/puts under concurrent crypto load.
