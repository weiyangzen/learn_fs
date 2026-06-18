# sources/distributed-fs/ceph-client/include/linux/power/bq27xxx_battery.h

Purpose: declares the shared bq27xxx fuel-gauge core interface and device data used by bus-specific drivers.

Important APIs and types: `enum bq27xxx_chip` enumerates supported TI gauge variants. `struct bq27xxx_access_methods` defines bus callbacks for byte/word and bulk reads/writes. `struct bq27xxx_reg_cache` caches capacity and flags. `struct bq27xxx_device_info` stores device pointer, chip type, options, name, data-memory registers, unseal key, bus methods, cache, design charge/voltage limits, removed flag, update timestamp, last status, delayed work, registered battery power_supply, global list node, mutex, and register map pointer. APIs update, setup, teardown the battery and expose PM ops.

Control flow: an I2C/HDQ/platform bus driver fills `bq27xxx_device_info` with chip identity and access callbacks, calls setup to register the power_supply and delayed polling, then update reads gauge registers into cache/status. Teardown marks removal, cancels work, and unregisters state.

State and persistence: runtime gauge state includes cached properties, delayed update work, removal flag, power_supply handle, lock, and bus callbacks. Gauge calibration/state may persist in chip data flash, but this header only describes kernel access.

Dependencies and integration points: integrates with the power_supply class, delayed work, bus-specific read/write implementations, chip data-memory definitions, mutex/list management, and PM suspend/resume hooks.

Risks and test signals: risks include bus callback failures, stale cache after removal, delayed work racing teardown, wrong chip register map, unseal-key misuse, and power_supply property unit mistakes. Test setup/teardown, periodic update, suspend/resume, all bus access paths, removal during work, chip variant register selection, and power_supply property reads.
