# sources/distributed-fs/ceph-client/include/linux/vbox_utils.h

## Purpose
This header declares VirtualBox guest utility logging, HGCM call helpers, status conversion, and guest-device reference helpers.

## Important APIs, types, and functions
Important APIs are `vbg_info()`, `vbg_warn()`, `vbg_err()`, `vbg_err_ratelimited()`, `vbg_debug`, `vbg_hgcm_connect()`, `vbg_hgcm_disconnect()`, `vbg_hgcm_call()`, `vbg_status_code_to_errno()`, `vbg_get_gdev()`, and `vbg_put_gdev()`.

## Control flow, state, and persistence
VirtualBox guest clients get the shared guest device, connect to an HGCM service, perform calls with requestor/client IDs and parameters, then disconnect and drop references. Logging goes both to VirtualBox backdoor channels and kernel printk variants depending on build/debug configuration. State is runtime guest-device and HGCM session state.

## Dependencies and integration points
It depends on printk and VirtualBox VMMDev type definitions. It integrates vboxguest core with vboxsf and other guest service clients.

## Risks and test signals
Risks include leaked guest-device references, untranslated VirtualBox status codes, logging from inappropriate contexts, and HGCM parameter count/timeout mistakes. Tests should cover connect/call/disconnect success and failure, errno mapping, ratelimited logging, and reference balancing.
