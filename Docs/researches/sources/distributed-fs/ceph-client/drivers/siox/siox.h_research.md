# sources/distributed-fs/ceph-client/drivers/siox/siox.h

Purpose: private SIOX core/master header. It defines the internal `struct siox_master` and helper APIs used by SIOX bus masters and the core.

Important types and APIs: `struct siox_master` contains driver-initialized fields `busno`, `pushpull`, optional `poll_interval`, plus framework-private lock, active flag, owner, embedded device, device list, concatenated buffers, status byte, last poll, and poll thread. `to_siox_master` and `siox_master_get_devdata` map devices to master state and driver-private storage. Declarations cover allocation, managed allocation, register/unregister, and managed register helpers.

Control flow support: bus master drivers allocate a master with extra private data, fill `pushpull` and bus number, then register it. The core owns the embedded device lifetime and polling state after registration.

State and dependencies: this header shapes all master runtime state. Dependencies include kthreads, mutex/list/device fields from kernel headers, and public `linux/siox.h` for device/driver types. Risks are exposing framework-private fields to master drivers, lifetime around `put_device`, and ABI fragility if fields are used outside intended core paths. Test signals are successful compilation of core and GPIO master, correct driver-private data pointer, and register/unregister lifetime tests.
