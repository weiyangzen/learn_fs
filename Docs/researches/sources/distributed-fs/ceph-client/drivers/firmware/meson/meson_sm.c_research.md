# sources/distributed-fs/ceph-client/drivers/firmware/meson/meson_sm.c

Purpose: Provides an Amlogic Meson secure monitor interface for SMC calls, shared-memory read/write operations, child device population, and serial-number sysfs exposure.

Important APIs/types/functions: `meson_sm_chip` maps abstract command indexes to SMC IDs and shared-memory base commands. `meson_sm_firmware` stores chip data and mapped in/out shared memory. Exports `meson_sm_call()`, `meson_sm_call_read()`, `meson_sm_call_write()`, and `meson_sm_get()`. `serial_show()` reads chip ID data.

Control flow: Probe matches a DT compatible, maps secure monitor shared-memory bases by calling SMC commands, stores firmware state, populates child OF devices, and exposes `serial`. Generic call lookup translates command indexes to SMC IDs, then calls `arm_smccc_smc()`. Read/write helpers move data through shared memory and validate firmware-reported sizes.

State and persistence behavior: Per-platform-device firmware state holds ioremapped shared memory and chip command table. Secure monitor state is external and can include efuse/chip/power-control effects depending on command.

Dependencies and integration points: Depends on ARM SMCCC, OF/platform devices, ioremap, sysfs device groups, and public Meson firmware headers. Consumers obtain a firmware pointer via DT node with `meson_sm_get()`.

Risks and test signals: Shared memory mappings are manually unmapped only on probe failure paths; devm does not manage them after success. Size-zero read semantics intentionally copy the full requested buffer for some commands. Test SMC command lookup failures, read/write size bounds, serial sysfs output, child device population, and probe failure unmap paths.
