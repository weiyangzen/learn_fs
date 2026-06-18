## sources/distributed-fs/ceph/src/rgw/rgw_obj_manifest.cc

Purpose: implements object manifest iteration and implicit object-location calculation for RGW head, shadow, and multipart tail objects.

Important APIs/functions: `RGWObjManifest::obj_iterator::operator++()` advances to the next object extent; `seek()` positions by logical offset; `update_explicit_pos()` handles explicit object maps; `update_location()` resolves the current `rgw_obj_select`; `get_implicit_location()` derives physical object names/namespaces for implicit layouts.

Control flow: explicit manifests iterate over `manifest->objs`. Implicit manifests treat offsets below head size as the head object, then use manifest rules to compute part id, stripe id, stripe offset/size, rule transitions, override prefixes, and tail placement. Multipart part/stripe naming uses `.<part>` in multipart namespace for first stripes and `.<part>_<stripe>` in shadow namespace for later stripes.

State and persistence: manifests store layout rules, object size, head/tail placement, prefix, tail instance, and explicit object maps elsewhere; this file mutates iterator state only. Location calculation determines where object data is read/written in RADOS.

Dependencies/integration: depends on RADOS `RGWObjManifest` declaration and bucket namespace constants `RGW_OBJ_NS_SHADOW`/`RGW_OBJ_NS_MULTIPART`.

Risks and test signals: off-by-one errors in stripe/part transitions can corrupt reads or writes. Tests should cover seeking into head/tail, zero-sized objects, explicit manifests, rule boundary offsets, multipart part transitions, override prefixes, tail placement bucket override, and max head size behavior.
