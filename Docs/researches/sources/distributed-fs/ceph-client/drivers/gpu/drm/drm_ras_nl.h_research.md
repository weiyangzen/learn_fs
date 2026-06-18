# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.h

Purpose: generated internal header declaring DRM RAS netlink handler prototypes and the generated family object.

Important APIs/types/functions: declares `drm_ras_nl_list_nodes_dumpit()`, `drm_ras_nl_get_error_counter_doit()`, `drm_ras_nl_get_error_counter_dumpit()`, and `extern struct genl_family drm_ras_nl_family`.

Control flow: no runtime control flow; it provides compile-time coupling between generated op tables, family registration, and manually implemented handlers.

State and persistence behavior: no state.

Dependencies and integration points: includes netlink/genetlink headers and UAPI `drm_ras.h`; consumed by `drm_ras.c`, `drm_ras_nl.c`, and `drm_ras_genl_family.c`.

Risks: generated header must stay synchronized with the YAML spec and generated C table. Prototype drift produces build failures or incorrect dispatch signatures.

Test signals: YNL regeneration, `make drivers/gpu/drm/`, include self-containment checks where configured, and command prototype changes reflected in all users.
