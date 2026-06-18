# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks_sed_ops.c

Purpose: Implements SED Opal boot PIN key read/write operations backed by PLPKS.

Important APIs/types/functions: Defines `struct plpks_sed_object_data`, constants for SED component/key/authority/range, `plpks_init_var()`, `sed_read_key()`, and `sed_write_key()`.

Control flow: First use lazily checks PLPKS availability. Reads initialize a PLPKS common variable, read the object into the fixed SED data format, convert the big-endian key length, copy the key out, nul-terminate it, and return the length. Writes populate the SED object metadata and key, remove any existing variable, then write the replacement variable.

State and persistence: Local booleans cache whether PLPKS was initialized and available. SED key material persists as a common PLPKS object under component `sed-opal`.

Dependencies and integration points: Depends on PLPKS core APIs and the SED Opal key interface declared in `linux/sed-opal-key.h`.

Risks: `sed_read_key()` bounds the copied key by `var.datalen`, not the fixed key array or caller buffer size, so callers must provide sufficient space. `sed_write_key()` copies `keylen` into a 32-byte array without local clamping, making caller validation critical. Name mangling for `opal-boot-pin` sets `var->name` to `/default/pri` but leaves `namelen` as the original key length, which deserves review.

Test signals: Read/write boot PIN with PLPKS unavailable, key lengths at 0/32/over-limit, replacement write after remove, default label mapping, endian round trips, and SED Opal unlock integration.

Source read size: 131 lines, 3546 bytes.
