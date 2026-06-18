# sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Makefile

## Purpose
This Makefile maps Sophgo pinctrl Kconfig symbols to kernel build objects. It builds the shared Sophgo common module and the individual SoC front-end modules.

## Important Build Rules
`obj-$(CONFIG_PINCTRL_SOPHGO_COMMON) += pinctrl-sophgo.o` creates the common composite object. `pinctrl-sophgo-objs += pinctrl-sophgo-common.o` always includes the shared core in that composite. Conditional object fragments add `pinctrl-cv18xx.o` or `pinctrl-sg2042-ops.o` when their helper-operation symbols are enabled. Individual front ends are built as `pinctrl-cv1800b.o`, `pinctrl-cv1812h.o`, `pinctrl-sg2000.o`, `pinctrl-sg2002.o`, `pinctrl-sg2042.o`, and `pinctrl-sg2044.o`.

## Control Flow
There is no runtime control flow. At build time, Kbuild evaluates each `obj-$()` and composite-object rule, then links helper operation objects into `pinctrl-sophgo.o` and compiles selected SoC drivers as separate objects or modules.

## State and Persistence
The file persists build composition. The common object owns shared operations; SoC-specific objects provide match tables and pin data that call into the common probe.

## Dependencies and Integration Points
It depends directly on the symbols from the adjacent `Kconfig`. The source files named here depend on shared headers such as `pinctrl-sophgo.h`, `pinctrl-cv18xx.h`, or SG2042 operation headers elsewhere in the Sophgo directory.

## Risks
If a SoC driver selects a helper symbol but the Makefile does not include the corresponding helper object in `pinctrl-sophgo.o`, module link failures or missing operation callbacks will result. Conversely, adding a new Kconfig symbol requires both an `obj-*` line and any helper-object wiring.

## Test Signals
Build every Sophgo symbol as built-in and module. Inspect module dependencies to ensure SoC modules resolve shared symbols from `pinctrl-sophgo`. Compile-test configurations should catch stale object names.
