# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/spmobj-attributes.c

Purpose: implements Secure Platform Management (SPM/Sure Admin) sysfs support for hp-bioscfg, including status reporting, signing/endorsement key provisioning, auth-token staging, and security buffer construction.

Important APIs/types/functions: `struct secureplatform_provisioning_data` mirrors WMI status data. `hp_calculate_security_buffer()` and `hp_populate_security_buffer()` build password or BEAM token authentication payloads. `update_spm_state()`, `statusbin()`, and `status_show()` query provisioning state. `sk_store()`, `kek_store()`, and `auth_token_store()` accept key/token writes. `hp_populate_secure_platform_data()` creates the SPM attribute group.

Control flow: SPM object creation initializes disabled state, queries firmware, clears key/token pointers, and creates sysfs files. Key stores copy the provided payload, send the matching secure-platform WMI command, update mechanism and reboot signal on success, then free the temporary key. Auth token store stages a token for the next BIOS setting update.

State and persistence: SPM keys provision firmware state; `auth_token` is in-memory and cleared by `hp_clear_all_credentials()`. `pending_reboot` is set after successful key changes.

Dependencies and integration: depends on `hp_wmi_perform_query()` from `biosattr-interface.c`, shared driver state, and the normal attribute set path that consumes `auth_token`.

Risks: `auth_token_store()` uses `kmemdup()` without appending a NUL byte, while later security-buffer helpers call `strlen()` on the token. Status output formats numeric key modulus bytes as text despite comments mentioning base64. Test signals include SPM absent/provisioned states, BEAM and UTF-prefix authentication buffer sizing, key provisioning return codes, token lifecycle, and reboot uevent emission.
