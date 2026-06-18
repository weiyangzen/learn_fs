# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb5.h

## Purpose

This header declares a large dynamic-binding surface for Kerberos 5 (`krb5_32.dll` or `krb5_64.dll`). It lets OpenAFS Windows code use MIT KFW/KRB5 functions through function pointers discovered with `LoadFuncs()` rather than through static linking.

## Important APIs, Types, and Functions

- `KRB5_DLL` selects `krb5_64.dll` on `_WIN64`, otherwise `krb5_32.dll`.
- Memory ownership APIs cover `krb5_free_principal`, `krb5_free_authenticator`, `krb5_free_addresses`, `krb5_free_authdata`, `krb5_free_ticket(s)`, `krb5_free_kdc_req/rep`, `krb5_free_cred(s)`, `krb5_free_keyblock(_contents)`, `krb5_free_data(_contents)`, `krb5_free_unparsed_name`, and related free routines.
- Crypto and checksum APIs include `krb5_c_encrypt`, `krb5_c_decrypt`, `krb5_c_encrypt_length`, `krb5_c_block_size`, `krb5_c_make_random_key`, `krb5_c_random_make_octets`, `krb5_c_random_seed`, `krb5_c_string_to_key`, `krb5_c_enctype_compare`, `krb5_c_make_checksum`, `krb5_c_verify_checksum`, and `krb5_c_keyed_checksum_types`.
- Context, principal, realm, and configuration APIs include `krb5_init_context`, `krb5_free_context`, `krb5_parse_name`, `krb5_unparse_name`, `krb5_set_principal_realm`, `krb5_principal_compare`, `krb5_build_principal(_ext)`, `krb5_get_default_realm`, `krb5_set_default_realm`, `krb5_get_host_realm`, `krb5_get_realm_domain`, `krb5_get_default_config_files`, and realm iterators.
- Credential acquisition and validation APIs include `krb5_get_in_tkt`, password/skey/keytab variants, `krb5_get_init_creds_password`, `krb5_get_init_creds_keytab`, option setters, `krb5_verify_init_creds`, `krb5_get_validated_creds`, `krb5_get_renewed_creds`, and password-change helpers.
- Credential cache and keytab APIs include `krb5_cc_resolve`, `krb5_cc_default(_name)`, `krb5_cc_set_default_name`, `krb5_cc_initialize`, `krb5_cc_destroy`, `krb5_cc_store_cred`, `krb5_cc_retrieve_cred`, `krb5_cc_start_seq_get`, `krb5_cc_next_cred`, `krb5_cc_end_seq_get`, `krb5_cc_remove_cred`, `krb5_kt_resolve`, `krb5_kt_default`, `krb5_kt_get_entry`, and keytab sequence functions.
- Protocol helpers include `krb5_mk_req`, `krb5_mk_req_extended`, `krb5_rd_req`, `krb5_mk_rep`, `krb5_rd_rep`, `krb5_mk_safe`, `krb5_rd_safe`, `krb5_mk_priv`, `krb5_rd_priv`, `krb5_sendauth`, `krb5_recvauth`, credential forwarding and credential message functions.
- Compatibility and diagnostics include `krb5_425_conv_principal`, `krb5_524_conv_principal`, `krb5_decode_ticket`, `krb5_locate_kdc`, `krb5_get_error_message`, and `krb5_free_error_message`.

## Control Flow

Like the other loadfuncs headers, this file only declares pointer types. The expected flow is: assemble a `FUNC_INFO` table for these symbol names, call `LoadFuncs(KRB5_DLL, ...)`, then route all KRB5 operations through `p<symbol>` variables. The groups in the file roughly follow free functions, crypto, validation helpers, context/authentication, string conversions, initial credential APIs, realm iteration, and lower-level cache/keytab routines.

## State and Persistence Behavior

The declarations expose stateful KRB5 objects: `krb5_context`, `krb5_auth_context`, credential caches, keytabs, replay caches, allocated principals/data, and credential structures. The header persists only process-global function pointers in consumers; the external DLL owns contexts, allocations, config discovery, default realm state, and cache/keytab persistence. Many APIs return allocated objects that must be released with matching `krb5_free_*` calls.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<krb5.h>`, including KRB5 calling-convention macros. It integrates OpenAFS with MIT Kerberos for Windows, credential cache management, ticket acquisition, auth context setup, AP-REQ/AP-REP exchange, password change, keytab access, and KRB4/KRB5 conversion compatibility.

## Risks

- The header mirrors a particular KFW/MIT Kerberos ABI. Symbol drift across installed Kerberos versions can cause partial loads.
- Function-pointer declarations must exactly match calling convention and parameter types; mismatches are runtime-critical on Windows.
- A partial load must not be treated as full capability; every consumer of less common APIs should handle NULL function pointers.
- Memory ownership is complex: many APIs allocate nested KRB5 objects that require a matching free routine from the same DLL instance.
- Some declarations are explicitly marked as not present in `krb5.h` or "more", increasing risk of version-specific exports.
- Crypto and credential APIs manipulate sensitive key/password data and should avoid logging buffers or leaving copied plaintext in long-lived memory.

## Test Signals

Compile tests should cover both `_WIN64` and 32-bit DLL name selection. Loader tests should verify all expected symbols against supported KFW versions and should explicitly exercise partial-load behavior. Integration tests should cover context initialization/free, ccache default resolution, principal parse/unparse, initial credential option setup, and matching free routines under leak detection.
