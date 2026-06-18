# sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc.c

Purpose: Small C library wrapping AMD Secure Processor Dynamic Boost Control ioctls for Python ctypes.

Important APIs, types, and functions: `get_nonce()` wraps `DBCIOCNONCE`, optionally copying a signature and returning nonce bytes. `set_uid()` wraps `DBCIOCUID`. `process_param()` wraps `DBCIOCPARAM`, passes message index/signature/parameter, then returns updated parameter and signature.

Control flow: Each function asserts required pointers, populates the corresponding UAPI struct, invokes ioctl, returns `errno` on failure or 0 on success, and copies output fields back to caller buffers.

State and persistence: Mutates device state through `/dev/dbc` ioctls. No local persistence.

Dependencies and integration points: Depends on `linux/psp-dbc.h` and is consumed by `dbc.py`. Integrates with AMD PSP DBC kernel driver.

Risks: `assert()` checks disappear under `NDEBUG`, so invalid null pointers could crash. Return value is positive errno, matching Python wrapper expectations but not typical negative errno convention. `process_param()` initializes `param` from `*data`, so caller must always pass a valid data pointer.

Test signals: ctypes calls against supported `/dev/dbc`, invalid signatures, invalid ioctl payload tests in `test_dbc.py`, and no-device handling at Python layer.
