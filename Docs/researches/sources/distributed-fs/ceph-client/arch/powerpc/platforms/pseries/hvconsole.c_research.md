# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvconsole.c

Purpose: Provides low-level PowerVM LPAR virtual terminal character I/O helpers for hvc console drivers.

Important APIs/types/functions: Exports `hvc_get_chars()` and `hvc_put_chars()`.

Control flow: `hvc_get_chars()` issues `H_GET_TERM_CHAR`, copies two returned big-endian 64-bit words into the caller buffer, and returns the firmware byte count on success or zero otherwise. `hvc_put_chars()` clamps count to firmware maximum, sends up to 16 bytes through `H_PUT_TERM_CHAR`, and maps `H_SUCCESS`, `H_BUSY`, and other errors to count, `-EAGAIN`, or `-EIO`.

State and persistence: No local state is retained. Data movement is through caller buffers and hcall return registers.

Dependencies and integration points: Depends on `plpar_hcall()`/`plpar_hcall_norets()`, hvc console core, PowerVM virtual terminal hcalls, and endian conversion of 16-byte payload chunks.

Risks: Callers must supply a buffer large enough for two unsigned long words even when requesting fewer bytes. Failed get operations discard error detail by returning zero. The helpers assume hcall payload alignment compatible with casting `u8 *` to `unsigned long *`.

Test signals: HVC console input/output on pseries LPAR, busy retry behavior, max-count clamping, unaligned buffer audits, and console stress during boot/panic are relevant.

Source read size: 75 lines, 1941 bytes.
