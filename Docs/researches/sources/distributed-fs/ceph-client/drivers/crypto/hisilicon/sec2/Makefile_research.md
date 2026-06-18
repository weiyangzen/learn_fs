# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/Makefile

## Purpose
This Makefile builds the newer QM-backed HiSilicon SEC2 crypto driver when `CONFIG_CRYPTO_DEV_HISI_SEC2` is enabled.

## Important APIs, types, and functions
It declares `hisi_sec2.o` and links it from `sec_main.o` and `sec_crypto.o`. There are no runtime APIs in the Makefile itself.

## Control flow
Kbuild selects these objects only when the SEC2 config symbol is enabled. `sec_main.o` is expected to own device/QM integration while `sec_crypto.o` owns algorithm request processing using the structures declared in `sec.h`.

## State and persistence behavior
The file has build-time state only. It does not create runtime storage.

## Dependencies and integration points
It depends on Kbuild and `CONFIG_CRYPTO_DEV_HISI_SEC2`. It integrates the SEC2 driver with the shared HiSilicon QM code built elsewhere in the hisilicon crypto tree.

## Risks and edge cases
Object names must stay aligned with source files. Enabling SEC2 without the shared QM support it depends on would fail at link or runtime through unresolved symbols or missing device support.

## Test signals
Build with `CONFIG_CRYPTO_DEV_HISI_SEC2=y` and `=m`; verify `hisi_sec2` links against `sec_main.o`, `sec_crypto.o`, and shared QM symbols.
