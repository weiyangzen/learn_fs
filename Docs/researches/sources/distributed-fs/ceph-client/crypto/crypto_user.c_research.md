# sources/distributed-fs/ceph-client/crypto/crypto_user.c

## Purpose
`crypto_user.c` implements the userspace configuration and reporting API for the Linux kernel crypto subsystem over `NETLINK_CRYPTO`. It lets privileged userspace add, remove, and reprioritize crypto algorithms or instances, delete the default RNG, and query or dump algorithm metadata. It is control-plane code, not data-plane cryptography.

## Important APIs, Types, And Functions
- `struct crypto_dump_info` carries the input skb, output skb, netlink sequence, and reply flags used by single and dump reports.
- `crypto_alg_match()` scans `crypto_alg_list` under `crypto_alg_sem`, filters by `cru_type`/`cru_mask`, skips larvals, matches by driver name for exact requests or by algorithm name for non-exact lookups, and takes a module reference with `crypto_mod_get()`.
- `crypto_report_one()`, `crypto_report_alg()`, `crypto_report()`, and `crypto_dump_report()` format `CRYPTO_MSG_GETALG` replies, including priority and type-specific reports via `alg->cra_type->report` or the local cipher report fallback.
- `crypto_update_alg()`, `crypto_del_alg()`, `crypto_add_alg()`, and `crypto_del_rng()` implement the mutating netlink commands. Mutations require `CAP_NET_ADMIN`.
- `crypto_user_rcv_msg()` dispatches messages through `crypto_dispatch[]`, handles multipart dump setup with `netlink_dump_start()`, and parses attributes with `nlmsg_parse_deprecated()`.
- Per-net operations `crypto_netlink_init()` and `crypto_netlink_exit()` create and release `net->crypto_nlsk`.

## Control Flow
Incoming netlink packets enter `crypto_netlink_rcv()`, which serializes all configuration handling with `crypto_cfg_mutex`, then passes messages to `crypto_user_rcv_msg()`. GETALG with `NLM_F_DUMP` computes a conservative dump allocation from the number of registered algorithms and starts a netlink dump. Non-dump requests are size-checked against `crypto_msg_min[]`, parsed against `crypto_policy[]`, and dispatched to the selected `doit` handler. Reply generation builds one netlink message per algorithm and appends algorithm-specific attributes until the skb is full.

Add, update, and delete operations all find algorithms through `crypto_alg_match()`. `NEWALG` forces module lookup/loading through `crypto_alg_mod_lookup()` and optionally sets priority. `UPDATEALG` removes dependent spawns before modifying priority so templates are refreshed. `DELALG` only unregisters crypto template instances and refuses core algorithms or busy instances.

## State And Persistence
Persistent state is the global crypto algorithm registry and each net namespace's `crypto_nlsk` socket. The file does not persist data across reboot. It mutates in-memory algorithm priority, algorithm instance registration, and default RNG selection. References acquired by `crypto_alg_match()` are released with `crypto_mod_put()`.

## Dependencies And Integration Points
The file depends on kernel netlink, per-net namespaces, `crypto_alg_list`, `crypto_alg_sem`, template instance unregister helpers, RNG helpers, and type-specific crypto report callbacks. Userspace sees this through `NETLINK_CRYPTO` and `struct crypto_user_alg`/`CRYPTOCFGA_*` attributes from `<linux/cryptouser.h>`.

## Risks And Edge Cases
The main risk is control-plane privilege and registry integrity. The code explicitly rejects non-null-terminated `cru_name` and `cru_driver_name`, checks `CAP_NET_ADMIN` for mutations, refuses priority changes without exact driver matching, and prevents unregistering non-instance core algorithms. Dumping walks the global algorithm list under read lock; large registries can still lead to multi-message output and `-EMSGSIZE` driven pagination. Refcount threshold `> 2` is used to detect busy instances, so changes to reference ownership semantics would need careful review.

## Test Signals
Test coverage is indirect through crypto self-tests and userspace netlink tooling. Useful signals include successful `CRYPTO_MSG_GETALG` single and dump paths, rejection of malformed unterminated names, privilege failures for mutating commands, priority update effects on algorithm selection, and delete failures for busy or non-instance algorithms.
