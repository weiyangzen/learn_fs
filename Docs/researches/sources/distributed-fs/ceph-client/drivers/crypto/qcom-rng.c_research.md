<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qcom-rng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qcom-rng.c

Purpose: provides Qualcomm PRNG/TRNG support as a crypto RNG named `stdrng`/driver `qcom-rng`, with optional hwrng registration for true RNG-compatible devices.

Important APIs and functions: `qcom_rng_read()` polls `PRNG_STATUS` for data availability, reads 32-bit words from `PRNG_DATA_OUT`, rejects zero words, and copies full or partial words to the caller. `qcom_rng_generate()` enables the optional core clock, serializes reads under a mutex, disables the clock, and returns crypto RNG status. `qcom_rng_enable()` initializes LFSR clocks and enables legacy PRNG hardware unless already enabled. `qcom_rng_init()` binds transforms to the singleton probed device and runs enable unless match data says to skip. `qcom_hwrng_read()` exposes the same read path to hwrng.

Control flow: probe allocates device state, maps registers, gets optional clock, stores match data, sets global `qcom_rng_dev`, registers the crypto RNG, and optionally registers hwrng with quality 1024. Remove unregisters crypto RNG and clears the singleton.

State and persistence: `struct qcom_rng` stores mutex, MMIO base, clock, hwrng object, and match data. Global `qcom_rng_dev` is a singleton consumed by all crypto transforms.

Dependencies and integration: platform OF compatibles `qcom,prng`, `qcom,prng-ee`, `qcom,trng`, ACPI `QCOM8160`, optional core clock, crypto RNG API, hwrng API, and iopoll.

Risks and test signals: singleton design assumes one device. hwrng read path does not enable/disable the clock, relying on skip-init/TRNG hardware state or external clocking. Rejecting zero output may treat valid random words as hardware failure if zero is possible. Test crypto_rng generate sizes not divisible by four, timeout handling, PRNG enable path, PRNG-EE skip-init, TRNG hwrng registration, clock-gated reads, and remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qcom-rng.c -->
