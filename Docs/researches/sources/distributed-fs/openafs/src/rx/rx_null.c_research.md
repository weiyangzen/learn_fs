# Research: sources/distributed-fs/openafs/src/rx/rx_null.c

## sources/distributed-fs/openafs/src/rx/rx_null.c

### Purpose
`rx_null.c` implements the RX null security class, which performs no authentication, protection, or per-connection security behavior.

### Important Functions and State
- Static `null_ops` is a zeroed `struct rx_securityOps`, so all security operations are absent.
- Static `null_object` points at `null_ops`.
- `rxnull_NewServerSecurityObject` and `rxnull_NewClientSecurityObject` both return the singleton `null_object`.

### Control Flow and State
The functions simply return the address of the singleton object. `RXS_*` macros in `rx.h` treat absent operation pointers as no-op success/zero behavior.

### Dependencies and Integration Points
Depends on `rx.h` security class definitions. Used by services and clients that select `RX_SECIDX_NULL`.

### Risks and Edge Cases
- The singleton has no reference management in this file; users must not free it.
- Null security intentionally provides no authentication or packet protection.
- Because all ops are NULL, any caller expecting callbacks for setup/teardown must tolerate no-ops.

### Test Signals
Tests should verify null client/server objects are identical singleton pointers, calls succeed without security callbacks, and code does not attempt to release/free the singleton incorrectly.
