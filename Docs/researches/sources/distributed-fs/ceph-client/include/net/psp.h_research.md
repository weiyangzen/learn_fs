# sources/distributed-fs/ceph-client/include/net/psp.h

Purpose: umbrella include for PSP networking support that pulls in UAPI definitions plus PSP helper functions and core types.

Important APIs and types: this header intentionally declares no standalone APIs; it includes `<uapi/linux/psp.h>`, `net/psp/functions.h`, and `net/psp/types.h`.

Control flow: users include this top-level header when both PSP type definitions and helper functions are needed.

State and persistence: no state is stored here.

Dependencies and integration points: integrates the PSP UAPI with kernel-facing PSP device, association, skb, and socket helpers.

Risks and test signals: risk is mostly include-order or accidental code growth despite the comment directing code to subheaders. Test compile coverage for users including only this aggregate header.
