
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Kconfig

Purpose: Kconfig entry for the HiSilicon PCIe Tune and Trace driver.

Important APIs/types/functions: defines `CONFIG_HISI_PTT` as a tristate named "HiSilicon PCIe Tune and Trace Device". It depends on ARM64 or 64-bit compile-test, plus PCI, DMA, I/O memory, and perf events.

Control flow: selecting the option allows `Makefile` to build `hisi_ptt.o`. The help text describes an RCiEP device that tunes PCIe traffic and traces TLP headers to memory.

State and persistence: Kconfig selection persists in kernel build config only; no runtime state.

Dependencies and integration: integrates with kernel build system and the perf/PCI/DMA prerequisites used by `hisi_ptt.c`.

Risks: missing dependency constraints would cause build failures on unsupported architectures. Overly narrow constraints can hide compile-test coverage.

Test signals: build `=y`, `=m`, and `=n` on ARM64 and COMPILE_TEST 64-bit configurations.
