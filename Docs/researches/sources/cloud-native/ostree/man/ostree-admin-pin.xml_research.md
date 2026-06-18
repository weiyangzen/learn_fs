# sources/cloud-native/ostree/man/ostree-admin-pin.xml

Purpose: documents `ostree admin pin`, which explicitly retains a deployment at an index or symbolic selector.

Important APIs/types: required `INDEX`; option `--unpin/-u`; index may be numeric or `booted`, `pending`, or `rollback`.

Control flow: sets or clears pin state so cleanup/garbage collection preserves or releases the deployment.

State and persistence: mutates deployment metadata that affects future cleanup.

Dependencies and integration: integrates deployment retention, cleanup, rollback, and status indexing.

Risks and test signals: docs must match accepted symbolic indices and cleanup behavior. Signals are cleanup tests preserving pinned deployments and unpin tests enabling removal.
