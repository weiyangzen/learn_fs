<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/compat.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/compat.c

Purpose: Compatibility shim for legacy ISA PnP drivers that use old vendor/function numeric IDs.

Important APIs/types/functions: `pnp_convert_id()` converts ISA vendor/device words into seven-character PnP ID strings. `pnp_find_dev()` searches all PnP devices or devices on one card after an optional starting device. It exports `pnp_find_dev`.

Control flow: caller supplies card, vendor, function, and optional `from`. Function converts IDs, handles wildcard `ISAPNP_ANY_ID`, then walks either `pnp_global` or the card device list until a matching ID is found.

State/persistence: read-only traversal of global/card lists.

Dependencies/integration: public `linux/isapnp.h`, PnP global/card lists, and `compare_pnp_id()`.

Risks: traversal is not explicitly locked here, relying on stable enumeration lifetime for legacy users. ID conversion must match historical ISA PnP byte ordering.

Test signals: legacy driver lookup for exact IDs, wildcard IDs, and continuation with `from` across global and card-scoped searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/compat.c -->
