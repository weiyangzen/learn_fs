# sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_api.h

Purpose: defines the mechanism-independent GSS API used by SUNRPC RPCSEC_GSS and the registration interface for concrete mechanisms such as Kerberos.

Important APIs and types: `struct gss_ctx` binds a mechanism to an internal context plus slack/alignment. `struct rpcsec_gss_oid` and `rpcsec_gss_info` represent mechanism OID, QOP, and service. Main APIs import/delete contexts and perform MIC, verify, wrap, and unwrap operations over `xdr_buf`. `struct pf_desc` maps pseudoflavors to QOP/service/domain names. `struct gss_api_mech` describes a mechanism module, OID, name, ops, pseudoflavors, and upcall enctype string. `struct gss_api_ops` is the mechanism callback table.

Control flow: auth code looks up a mechanism by OID/name/pseudoflavor, imports a context token, then dispatches MIC/wrap/unwrap operations through mechanism callbacks. Mechanisms are registered/unregistered dynamically and refcounted via `gss_mech_get()`/`put()`.

State and persistence: mechanism registrations and context internals are in-memory. Imported contexts carry expiration time but are not persistent.

Dependencies and integration points: integrates XDR buffers, RPC message protocol constants, module ownership, auth domains, and crypto mechanisms.

Risks and test signals: risks include mechanism refcount leaks, OID lookup mismatches, wrong slack/alignment for privacy wrapping, and context deletion races. Test with Kerberos pseudoflavors, module unload, MIC verification failures, privacy wrapping, and token import error paths.
