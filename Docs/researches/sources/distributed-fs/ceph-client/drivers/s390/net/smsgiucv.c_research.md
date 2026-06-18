# sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.c

Purpose: implements the z/VM IUCV special-message core driver. It connects to `*MSG`, receives CP SMSG traffic, dispatches messages by prefix to registered callbacks, and exports callback registration APIs.

Important APIs and functions: exports `smsg_register_callback()` and `smsg_unregister_callback()`. IUCV callbacks are `smsg_path_pending()` and `smsg_message_pending()` in `smsg_handler`. Module lifecycle is `smsg_init()` and `smsg_exit()`.

Control flow: module init requires `machine_is_vm()`, registers an IUCV bus driver and handler, allocates/connects an IUCV path to `*MSG`, then issues `SET SMSG IUCV`. Incoming paths are accepted only from `*MSG`. Incoming messages are received into a DMA-capable buffer, converted from EBCDIC to ASCII, split into sender and payload, trimmed for sender whitespace, and dispatched to the first callback whose prefix matches the payload.

State and persistence: global state consists of `smsg_path` and a spinlock-protected callback list. It is runtime only; module exit disables SMSG delivery with `SET SMSG OFF`, unregisters IUCV, and unregisters the driver.

Dependencies and integration: depends on z/VM, IUCV core, CP command support, EBCDIC conversion, and consumers such as `smsgiucv_app.c`. Exported symbols allow other modules to receive prefixed SMSGs.

Risks: callbacks run while `smsg_list_lock` is held in message context, so callback implementations must be non-blocking and avoid re-entering registration. Only the first prefix match is invoked. Allocation failure rejects the IUCV message. Prefix pointers are not copied, so callers must keep prefix storage valid until unregister.

Test signals: module load outside z/VM returns protocol unsupported, successful path connect issues SMSG mode, callback registration/unregistration ordering, EBCDIC sender trimming, prefix dispatch, receive allocation failure path, and module unload cleanup.
