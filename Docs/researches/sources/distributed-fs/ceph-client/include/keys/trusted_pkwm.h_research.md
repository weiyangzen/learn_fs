# sources/distributed-fs/ceph-client/include/keys/trusted_pkwm.h

Source read summary: 34 lines, 799 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_pkwm.h` defines PKWM trusted-key option bits and parsed option storage for hardware-wrapped keys.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `trusted_pkwm_options`. Important constants/macros: none.

Control flow: The PKWM backend reads `trusted_pkwm_options` from trusted-key option parsing to decide whether to create new wrapped material, load an existing blob, or use hardware-specific policy flags.

State and persistence behavior: Options are transient parse state; resulting wrapped keys persist in the trusted-key payload.

Dependencies and integration points: It includes `keys/trusted-type.h`, `linux/bitops.h`, `linux/printk.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Unknown option bits or inconsistent create/load state can make a wrapped key unusable or weaken policy expectations.

Test signals: Test PKWM option parsing, create/load flows, invalid bit rejection, and integration with the common trusted key type.
