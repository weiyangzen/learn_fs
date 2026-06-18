## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_krb5.h

Purpose: Kerberos-specific GSS-API extension header for mechanism OIDs, Kerberos name OIDs, credential/cache helpers, enctype restrictions, and lucid context export.

Important APIs/types/functions: Declares Kerberos mechanism OIDs (`gss_mech_krb5`, old/wrong variants, mechanism sets), Kerberos name OIDs, `gss_uint64`, lucid key/context structs (`gss_krb5_lucid_key_t`, RFC1964 and CFX keydata, `gss_krb5_lucid_context_v1_t`), and APIs `krb5_gss_register_acceptor_identity`, `gss_krb5_get_tkt_flags`, `gss_krb5_copy_ccache`, `gss_krb5_ccache_name`, `gss_krb5_set_allowable_enctypes`, `gss_krb5_export_lucid_sec_context`, and freeing helpers.

Control flow: Applications can set acceptor identity, acquire/copy Kerberos credentials into a ccache, restrict negotiated enctypes before `gss_init_sec_context`, and export an established context into readable key/sequence fields for protocol integrations.

State and persistence: Ccache name changes and acceptor identity are process/global library state. Exported lucid context memory is caller-owned until freed through the matching GSS extension. Ccache operations may persist credentials in the selected Kerberos cache.

Dependencies and integration points: Includes `gssapi.h` and `krb5.h`; tightly integrates GSS with Kerberos credential caches, key enctypes, and OpenAFS/Kerberos token workflows.

Risks: Lucid context export invalidates or consumes the original context handle as documented. Exported keys are sensitive material and must be freed promptly. Old/wrong OIDs exist for compatibility and can cause negotiation surprises.

Test signals: Register acceptor identity, copy credentials to a ccache, set allowable enctypes before context creation, inspect ticket flags, export/free lucid contexts for both RFC1964 and CFX protocols, and verify sensitive buffers are released.
