# sources/distributed-fs/ceph-client/include/linux/pruss_driver.h

Purpose: declares the TI PRU-ICSS subsystem helper interface for PRUSS memory regions and configuration registers used by remoteproc-backed PRU clients.

Important APIs and types: enums describe GP mux selection, GPI modes, PRU core types, and PRUSS memory ranges. `struct pruss_mem_region` carries virtual, physical, and size information. `struct pruss` stores device/config mappings, regmap, memory region ownership, a mutex, and clock mux handles. APIs include `pruss_get()`, `pruss_put()`, `pruss_request_mem_region()`, `pruss_release_mem_region()`, GPMUX get/set, GPI mode setting, MII_RT enable, and XFR enable. Disabled builds return `-EOPNOTSUPP` or `ERR_PTR(-EOPNOTSUPP)`.

Control flow: a PRU remoteproc client obtains the parent PRUSS, requests a memory region, configures mux/mode or feature bits, uses the memory while holding ownership, then releases it and drops the PRUSS reference.

State and persistence: runtime state is the PRUSS device object, mapped memories, `mem_in_use[]` ownership, mutex serialization, and hardware configuration registers. Hardware settings persist until changed or reset by platform power management.

Dependencies and integration points: depends on remoteproc PRUSS IDs, regmap, clocks, device model, and TI PRUSS platform drivers. It integrates industrial Ethernet, real-time co-processor firmware, and PRU memory sharing.

Risks and test signals: risks include double allocation of PRUSS memory, SoC-specific mux value differences, unbalanced get/put, register writes racing without the PRUSS lock, and config-disabled callers mishandling `-EOPNOTSUPP`. Test concurrent memory requests, GPMUX/GPI programming on supported SoCs, remoteproc probe/remove, and non-PRUSS build coverage.
