<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Kconfig -->
# sources/distributed-fs/ceph-client/lib/vdso/Kconfig

## Purpose
Kconfig options that gate the generic vDSO support library, generic gettimeofday implementation, optional overflow protection, and vDSO getrandom support.

## APIs, Types, and Functions
Defines `HAVE_GENERIC_VDSO`, `GENERIC_GETTIMEOFDAY`, `GENERIC_VDSO_OVERFLOW_PROTECT`, and `VDSO_GETRANDOM`. The latter three are visible only inside `if HAVE_GENERIC_VDSO`.

## Control Flow, State, and Persistence
This is declarative configuration. Architectures select `HAVE_GENERIC_VDSO` and then select the relevant feature bools. Help text documents that generic gettimeofday requires architecture fallback implementations, overflow protection adds a hot-path conditional, and getrandom is selected by supporting architectures.

## Dependencies and Integration
Integrates with architecture Kconfig files, `lib/vdso/Makefile`, generic vDSO time code, and random vDSO code. These symbols control compilation and code paths in `datastore.c`, `gettimeofday.c`, and `getrandom.c`.

## Risks and Test Signals
Risks include selecting generic gettimeofday without required arch fallback hooks, enabling overflow protection with measurable hot-path cost, or selecting getrandom without architecture support glue. Test signals are architecture allmodconfig/build coverage, vDSO ABI tests, syscall fallback tests, and config matrix builds for each bool combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Kconfig -->
