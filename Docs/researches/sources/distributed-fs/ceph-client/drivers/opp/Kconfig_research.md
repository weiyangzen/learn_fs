# sources/distributed-fs/ceph-client/drivers/opp/Kconfig

## Purpose
Defines the boolean `PM_OPP` configuration symbol for the Operating Performance Points framework.

## Important APIs, types, and functions
Contains `config PM_OPP` and help text describing frequency/voltage OPP tuples per voltage domain, with a pointer to `Documentation/power/opp.rst`.

## Control flow
No runtime control flow. Kconfig evaluates whether `CONFIG_PM_OPP` is selected by other symbols.

## State and persistence behavior
The persistent effect is build configuration state that enables OPP framework compilation and consumers.

## Dependencies and integration points
Integrates with `drivers/opp/Makefile` and SoC/power-management users that select or depend on OPP support.

## Risks and edge cases
Because this symbol has no prompt in this file, correctness depends on external selectors. Help text drift is the main file-local maintenance risk.

## Test signals
Builds with `CONFIG_PM_OPP` selected should compile the OPP objects selected by the Makefile.
