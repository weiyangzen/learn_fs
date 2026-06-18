# sources/distributed-fs/lustre-release/include/linux/lnet/api.h

Purpose: kernel-only public LNet API header. It exposes initialization, addressing, match-entry, memory-descriptor, data movement, and control operations for Lustre Networking.

Important APIs/types: initialization uses `LNetNIInit()` and `LNetNIFini()`. Addressing helpers include `LNetGetId`, `LNetDist`, primary/local NID helpers, peer-local/discovery checks, NID fetch callbacks, local-net checks, and NID update callback registration. Match and memory APIs include `LNetMEAttach`, `LNetMDAttach`, `LNetMDBind`, and `LNetMDUnlink`. Data movement uses asynchronous `LNetPut` and `LNetGet` over portals/match bits and MD handles. Misc APIs cover lazy portals, generic `LNetCtl`, peer debugging, peer discovery status, and peer insertion.

Control flow: this header is declarative; implementations manage LNet lifecycle, portal/match tables, MD ownership, and asynchronous completion events. API users must initialize LNet before calls and bind/attach memory before PUT/GET operations.

State and persistence: API calls operate on kernel-global LNet state and transient handles. No on-disk persistence is defined.

Dependencies/integration: includes `uapi/linux/lnet/lnet-types.h`, rejects non-kernel inclusion, and is consumed by Lustre kernel modules and LNDs.

Risks and test signals: risks are lifecycle misuse, stale MD handles, incorrect large-NID handling, and data movement without matching portals. Test signals are NI init/fini refcounting, NID enumeration, ME/MD attach/unlink events, PUT/GET success/failure paths, lazy portal behavior, and peer discovery callbacks.
