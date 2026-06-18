## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_api.c

Purpose: exposes the `/dev/pkey` misc-device ioctl ABI and in-kernel `pkey_key2protkey()` service. It validates user requests, copies key material and APQN lists, delegates crypto operations to registered pkey handlers, and scrubs sensitive buffers.

Important APIs/types/functions: exported `pkey_key2protkey()` and ioctl handlers for `PKEY_GENSECK`, `PKEY_CLR2SECK`, `PKEY_SEC2PROTK`, `PKEY_CLR2PROTK`, `PKEY_FINDCARD`, `PKEY_SKEY2PKEY`, `PKEY_VERIFYKEY`, `PKEY_GENPROTK`, `PKEY_VERIFYPROTK`, `PKEY_KBLOB2PROTK`, `PKEY_GENSECK2`, `PKEY_CLR2SECK2`, `PKEY_VERIFYKEY2`, `PKEY_KBLOB2PROTK2`, `PKEY_APQNS4K`, `PKEY_APQNS4KT`, and `PKEY_KBLOB2PROTK3`.

Control flow: `key2protkey()` first tries a direct key-based handler and then slowpath handlers. `pkey_key2protkey()` additionally requests handler modules on `-ENODEV` and retries. Ioctls copy fixed structures from userspace, optionally copy variable key/APQN arrays, call pkey handler wrapper functions, copy results back, and zero local sensitive structures. The misc device is registered in `pkey_api_init()` and removed in `pkey_api_exit()`.

State and persistence: this file keeps little persistent state beyond the miscdevice. Sensitive key buffers are temporary and freed with `kfree_sensitive()` or wiped with `memzero_explicit()`. Handler registry state lives in `pkey_base.c`.

Dependencies and integration: uses Linux miscdevice, usercopy helpers, pkey UAPI structs, zcrypt CCA token definitions, and pkey handler dispatch wrappers.

Risks and test signals: risks are ABI validation gaps, incorrect buffer length negotiation, missed scrubbing, unbounded APQN counts from user input, and fallback behavior masking handler-specific errors. Test every ioctl success and failure path, small output buffers, NULL optional pointers, unsupported key sizes/types, module autoload retry, and KASAN/usercopy validation.
