## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.h

Purpose: defines shared pkey constants, token layouts, key-size helpers, handler interface, and handler dispatch prototypes used by pkey API and hardware-specific handlers.

Important APIs/types/functions: constants include `KEYBLOBBUFSIZE`, `MINKEYBLOBBUFSIZE`, `PROTKEYBLOBBUFSIZE`, `MAXAPQNSINLIST`, and `AES_WK_VP_SIZE`. Token views include `struct protkeytoken`, `struct protaeskeytoken`, and `struct clearkeytoken`. Helper functions map AES key types/sizes. `struct pkey_handler` defines callbacks for support checks, conversion, generation, clear-to-key, verification, and APQN discovery.

Control flow: API code calls dispatch wrappers declared here; handlers implement the callback table and register/unregister with `pkey_handler_register()` and `pkey_handler_unregister()`. Support-check callbacks must be non-sleeping because they run under RCU read lock.

State and persistence: no storage is owned here except external debug declarations. The handler structure embeds a list node used by the base registry.

Dependencies and integration: includes s390 pkey UAPI and debug definitions. Shared by pkey base, pkey API, and pkey handler modules such as CCA.

Risks and test signals: risks are mismatched token layout packing, callback sleep violations under RCU, and inconsistent keytype/size mapping. Test compile coverage for all handlers, verify packed token sizes against UAPI expectations, and exercise AES/ECC/HMAC size helper mappings.
