# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_debug.h

## Purpose
`zcrypt_debug.h` centralizes zcrypt debug-facility levels, convenience macros, the global debug handle declaration, and debug subsystem lifecycle prototypes.

## Important APIs, Types, And Functions
It defines `DBF_ERR`, `DBF_WARN`, `DBF_INFO`, `DBF_DEBUG`, helper mappings `RC2ERR()` and `RC2WARN()`, maximum sprintf argument metadata, and wrappers `ZCRYPT_DBF()`, `ZCRYPT_DBF_ERR()`, `ZCRYPT_DBF_WARN()`, and `ZCRYPT_DBF_INFO()`. It declares `extern debug_info_t *zcrypt_dbf_info`, `zcrypt_debug_init()`, and `zcrypt_debug_exit()`.

## Control Flow
The macros directly invoke `debug_sprintf_event()` against `zcrypt_dbf_info`; callers control when and at which level events are emitted. There is no branching logic except the `RC2*` level selection helpers.

## State And Persistence
The global debug handle is external state managed by the zcrypt debug implementation. Debug records are kernel debug-facility records, not persistent repository state.

## Dependencies And Integration Points
The header depends on `asm/debug.h` and is included broadly by zcrypt helpers, message handlers, error conversion, and queue management. It standardizes log severity across this driver family.

## Risks And Test Signals
Risks include using debug macros before initialization, format/argument mismatches, and overly noisy logs at high-frequency paths. Build-time format checking is limited because these are macros; runtime signals include debugfs/debug facility output and clean init/exit of the global debug area.
