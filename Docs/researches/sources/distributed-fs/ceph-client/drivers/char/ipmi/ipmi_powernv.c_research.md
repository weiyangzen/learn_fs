# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_powernv.c

Purpose: This is the PowerNV OPAL-backed IPMI SMI transport. It registers an IPMI system interface for device-tree nodes compatible with `ibm,opal-ipmi` and translates the generic IPMI SMI handler calls into OPAL `opal_ipmi_send` and `opal_ipmi_recv` operations.

Important APIs, types, and functions: `struct ipmi_smi_powernv` stores the OPAL interface ID, registered `ipmi_smi`, IRQ, spinlock, one outstanding `ipmi_smi_msg`, and reusable `opal_ipmi_msg` buffer. The SMI handler table supplies `start_processing`, `sender`, `request_events`, `set_run_to_completion`, and `poll`. Driver entry points are `ipmi_powernv_probe`, `ipmi_powernv_remove`, and the platform driver declared by `module_platform_driver`.

Control flow: Probe reads `ibm,ipmi-interface-id` and interrupt data from device tree, maps or requests an OPAL event IRQ, allocates an OPAL message buffer, and registers the SMI with `ipmi_register_smi`. Sends validate message size and minimum netfn/cmd bytes, reject concurrent outstanding requests with `IPMI_NODE_BUSY_ERR`, format the OPAL message, call `opal_ipmi_send`, and retain the generic message as `cur_msg`. Interrupts or polling call `ipmi_powernv_recv`, which reads OPAL response data, validates size and format version, fills `msg->rsp`, clears `cur_msg`, and hands the message to `ipmi_smi_msg_received`.

State and persistence behavior: The driver keeps exactly one in-flight request per interface and one reusable OPAL buffer protected by `msg_lock`. There is no persistent storage. Device state exists for the lifetime of the platform device and registered SMI.

Dependencies and integration points: It integrates with the IPMI message handler via `ipmi_register_smi`/`ipmi_unregister_smi`, with the PowerNV OPAL firmware ABI via `opal_ipmi_send`, `opal_ipmi_recv`, and `opal_event_request`, with OF matching, and with Linux IRQ mapping/request/free APIs.

Risks and edge cases: The one-request model means upper layers can observe node-busy when a second message arrives before OPAL completion. Receive errors synthesize generic IPMI error replies, while `OPAL_EMPTY` is treated as a non-event for polling. If OPAL returns an undersized or unknown-version message, the current message is not completed in those branches, so future sends can remain blocked until another successful/error receive path clears it. Remove unregisters the SMI then frees IRQ/mapping; outstanding OPAL request handling during removal is a key integration risk.

Test signals: Validate OF probe with missing properties, IRQ map fallback to OPAL event request, send length validation, busy behavior with a pending request, successful OPAL response translation, `OPAL_EMPTY` polling behavior, OPAL error-to-completion-code synthesis, remove-time `ipmi_unregister_smi`, and recovery from malformed OPAL responses.
