# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.c

Purpose: central zcrypt user and kernel API implementation. It manages zcrypt device nodes, permission masks, message-type registration, queue/card selection, RSA/CCA/EP11 request dispatch, status ioctls, hwrng integration, AP-bus readiness waits, and module init/exit.

Important APIs and functions: `zcrypt_msgtype_register()`/`zcrypt_msgtype()` maintain crypto message operation providers. zcdn helpers create named char devices with per-node AP/ioctl masks. `zcrypt_open()` selects global or per-device permissions. `zcrypt_rsa_modexpo()` and `zcrypt_rsa_crt()` choose accelerator/CCA queues using card/queue load, request size, speed rating, permissions, and retry penalties. `_zcrypt_send_cprb()` and `_zcrypt_send_ep11_cprb()` prepare CCA/EP11 AP messages, enforce admin/usage-domain permissions, select eligible queues, and call provider ops. Exported `zcrypt_send_cprb()` and `zcrypt_send_ep11_cprb()` add retry and AP bus rescan behavior. Status helpers build masks and counters. `zcrypt_rng()` and hwrng callbacks fill a page buffer from CCA RNG requests. `zcrypt_wait_api_operational()` waits once for APQN bindings.

Control flow: ioctl dispatch first checks the node ioctl mask, then copies user structures, runs request-specific retry loops, optionally triggers AP bus rescan on `-ENODEV`, and copies results back. Queue selection is done under `zcrypt_list_lock`; selected card/queue/module/device refs are held during operation and dropped afterward.

State and persistence: module state includes card list, ops list, open count, zcdn device class/char-device minors, debug feature handle, RNG buffer/count, and one-shot API readiness state. It does not persist state across unload.

Dependencies and integration: depends on AP bus, zcrypt message type 6/50 providers, CCA/EP11 misc preparation helpers, tracepoints, misc/cdev device models, sysfs class attributes, hwrng, and AP permission masks.

Risks: queue-selection reference counting and lock boundaries are subtle. Per-node permission checks must distinguish admin control domains from usage domains. Retry and rescan behavior can mask transient AP binding races but must not livelock. User/kernel buffer handling depends on `ZCRYPT_XFLAG_USERSPACE`.

Test signals: ioctls with denied masks, per-zcdn AP/AQ/AD masks, RSA size bounds, CCA and EP11 target selection, `-EAGAIN` retry limit to `-EIO`, `-ENODEV` rescan retry, status mask compatibility ioctls, RNG register/read/remove, zcdn create/destroy conflicts, and init failure unwinding.
