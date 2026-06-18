# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_mech_switch.c

## Purpose
`gss_mech_switch.c` is the mechanism registry and dispatcher for SUNRPC GSS. It lets mechanism modules register supported OIDs and pseudoflavors, maps GSS tuples to pseudoflavors, registers server auth domains, imports security contexts, and dispatches generic GSS operations to mechanism-specific ops.

## Important APIs, Types, and Functions
Global state is `registered_mechs`, protected by `registered_mechs_lock` and traversed under RCU. Registration APIs are `gss_mech_register()` and `gss_mech_unregister()`. Lookup APIs include `gss_mech_get_by_name()`, `gss_mech_get_by_OID()`, and `gss_mech_get_by_pseudoflavor()`, with module autoload where needed. Mapping helpers include `gss_svc_to_pseudoflavor()`, `gss_mech_info2flavor()`, `gss_mech_flavor2info()`, `gss_pseudoflavor_to_service()`, `gss_pseudoflavor_to_datatouch()`, and `gss_service_to_auth_domain_name()`. Dispatch functions are `gss_import_sec_context()`, `gss_get_mic()`, `gss_verify_mic()`, `gss_wrap()`, `gss_unwrap()`, and `gss_delete_sec_context()`.

## Control Flow
Mechanism registration first calls `gss_mech_svc_setup()`, which creates `gss/<name>` auth domain names and registers each pseudoflavor with server-side GSS auth. The mechanism is then added to the RCU list. Client or server users look up by name, OID, or pseudoflavor, holding a module reference. Imported contexts allocate a generic `gss_ctx`, get the mechanism reference, and call the mechanism import op. Per-message functions then dispatch through `ctx->mech_type->gm_ops`.

## State and Persistence
Registered mechanisms persist on the global list until unregister. Each pseudoflavor descriptor may own an auth domain and allocated auth domain name. Generic `gss_ctx` objects persist per imported security context and hold a mechanism reference until `gss_delete_sec_context()`.

## Dependencies and Integration Points
It depends on module loading, OID formatting, SUNRPC server auth domain registration, GSS API structs, RPC auth pseudoflavors, tracepoints, RCU, and mechanism modules such as Kerberos. It connects client auth, server auth, and mechanism implementations.

## Risks and Edge Cases
Registration failure must unwind any auth domains already created. Lookups rely on module refs to keep mechanisms alive after RCU traversal. `gss_import_sec_context()` allocates `gss_ctx` before calling the mechanism; if a mechanism import fails after partial allocation, cleanup responsibility must be observed by callers and mechanism code. OID-to-module autoload uses a stringified OID, so alias correctness matters.

## Test Signals
Autoload and mapping can be tested by converting Kerberos OID/qop/service to krb5/krb5i/krb5p pseudoflavors and back. Runtime GSS calls validate dispatch. KUnit for Kerberos indirectly exercises lookup by enctype, while integration tests exercise mechanism registration and deletion.
