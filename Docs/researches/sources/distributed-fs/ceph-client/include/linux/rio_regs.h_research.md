# sources/distributed-fs/ceph-client/include/linux/rio_regs.h

Purpose: this header defines RapidIO configuration-space, extended feature, LP-Serial, error management, and switch routing table register offsets and bit masks.

Important APIs/types/functions: it defines the 16 MiB maintenance space size, standard CAR/CSR offsets for identity, assembly, processing element features, switch port info, source/destination ops, route limit, mailboxes, doorbells/write-port, logical-layer control, base address, device ID, host lock, component tag, and standard route config. Helper macros parse extended feature block headers and calculate per-port register offsets from port number and register map type. It also defines error management registers and switch routing table register fields.

Control flow: RapidIO enumeration and drivers read identity/capability registers, walk the extended feature list using `RIO_GET_BLOCK_PTR()`/`RIO_GET_BLOCK_ID()`, configure ports through LP-Serial registers, detect link/error state, enable error notifications, and program switch route tables.

State and persistence: no kernel state is stored. The constants describe persistent hardware register state in RapidIO devices and switches.

Dependencies and integration points: included by `rio.h` and RapidIO core/driver implementations. It integrates with maintenance transaction accessors from `rio_drv.h` and hardware-specific mport ops.

Risks: register offsets are specification ABI; mistakes can corrupt routing, error handling, or device enumeration. Some definitions are version-specific and register-map-type dependent. Test signals include config-space decode tests, EFB walking on devices with multiple blocks, port status/error management handling, switch route programming, and cross-checking route table size for 8-bit versus 16-bit dest IDs.
