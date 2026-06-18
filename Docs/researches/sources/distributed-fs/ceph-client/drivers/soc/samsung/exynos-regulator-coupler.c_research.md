# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-regulator-coupler.c

## Purpose

`exynos-regulator-coupler.c` registers an Exynos-specific regulator coupler for Exynos5800. It balances voltages across coupled regulators while preserving current voltage when consumers have not yet applied constraints.

## Important APIs, Types, and Functions

`regulator_get_optimal_voltage()` computes a safe target range for one regulator considering consumers, constraints, current voltages, and max-spread. `exynos_coupler_balance_voltage()` repeatedly picks the coupled regulator with the largest useful voltage delta and calls `regulator_set_voltage_rdev()`. `exynos_coupler_attach()` is a no-op. `exynos_coupler_init()` registers the coupler only on `samsung,exynos5800`.

## Control Flow

At arch init, machine compatibility is checked. During regulator coupling, the core calls `balance_voltage()`, which loops through coupled regulators under regulator locks, computes optimal voltages, applies the best next change, and repeats until no change is needed or an error occurs.

## State and Persistence Behavior

No private state is stored. Voltage changes mutate regulator hardware state through regulator core operations.

## Dependencies and Integration Points

It depends on OF machine matching and regulator coupler internals, including locked `regulator_dev` objects, consumer checks, and coupling constraints. It is tailored for Exynos5800 coupled rails.

## Risks and Edge Cases

The code uses regulator core internal-style helpers and assumes locks are held. The loop condition `while (n_coupled > 1)` relies on internal done-bit logic to exit through `!best_rdev`; regressions could spin if deltas never settle. Incorrect max-spread constraints can reject valid configurations or permit unsafe rail differences.

## Test Signals

Test on Exynos5800 with coupled CPU rails, including no consumer constraints, conflicting constraints, suspend-state balancing, voltage raise/lower paths, and max-spread violations. Use lockdep to verify regulator lock assumptions.
