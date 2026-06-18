
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/dummy_stm.c

Purpose: test STM device provider that discards packets and optionally fails links, useful for STM class/configfs/source testing without hardware.

Important APIs/types/functions: `dummy_stm_packet()` returns the packet size, optionally trace-printing under local DEBUG. Module parameters control `nr_dummies`, `fail_mode`, `master_min`, `master_max`, and `nr_channels`. `dummy_stm_link()` can reject channels based on `fail_mode`.

Control flow: init validates parameters, allocates names `dummy_stm.N`, fills `stm_data`, and registers each with `stm_register_device()`. Exit unregisters and frees names.

State and persistence: static array of up to 32 `stm_data` objects and allocated names. No trace data persistence.

Dependencies and integration: depends on generic STM core APIs and UAPI master/channel limits.

Risks: intended for testing; parameter combinations can create very large channel spaces. Failure injection is channel-bit based and should not be confused with hardware behavior.

Test signals: create policies against dummy devices, write through char/source paths, validate master/channel bounds, test link failures using `fail_mode`, and unload cleanup.
