# sources/distributed-fs/ceph-client/drivers/char/hw_random/via-rng.c

Purpose: x86 VIA PadLock/XSTORE hardware RNG driver.

Important APIs, types, and functions: inline `xstore()`, `via_rng_data_present()`, `via_rng_data_read()`, `via_rng_init()`, global `via_rng`, module init/exit, and x86 CPU feature table.

Control flow: module init requires `X86_FEATURE_XSTORE` and registers hwrng. Init enables legacy RNG through `MSR_VIA_RNG` except newer Nano CPUs where CPUID `XSTORE_EN` is required. Data-present executes `xstore` up to 20 times using 1-byte chunk mode, stores the resulting datum in `rng->priv`, and returns availability. Data-read returns the cached byte count as one byte.

State and persistence: global hwrng; transient random datum cached in `rng->priv`; legacy hardware enable persists in MSR until changed.

Dependencies and integration: x86 CPU feature detection, PadLock alignment rules, inline assembly, MSR access, delays, and hwrng core.

Risks and test signals: `rng->priv` is used as a data cache rather than pointer, so concurrency depends on hwrng serialization. Tests should cover feature absence, Nano path, MSR enable/readback, wait/non-wait polling, and module unregister.
