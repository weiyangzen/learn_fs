# sources/distributed-fs/lustre-release/lnet/lnet/lo.c

Purpose: implements the loopback LNet LND (`the_lolnd`). It delivers local messages back into the LNet parser without a real network transport and copies payload data directly between kernel IO vectors.

Important APIs/types/functions: `lolnd_send()` asserts the message is not routed or targeting a router and calls `lnet_parse()` with the local NI NID and original message. `lolnd_recv()` copies send message payload into the receive iterator with `lnet_copy_kiov2iter()`, finalizes the receive message if present, and always finalizes the original send message. `lolnd_startup()` and `lolnd_shutdown()` enforce a single `lolnd_instanced` instance. `the_lolnd` fills `struct lnet_lnd` operations for type `LOLND`.

Control flow: when LNet sends to loopback, `lolnd_send()` immediately re-enters receive parsing. If a matching receive buffer exists, `lolnd_recv()` copies data and finalizes both receive and send messages with status zero; if receiving is a discard path, it skips the receive copy/finalize and still completes the send. Startup/shutdown only toggle the instance flag.

State and persistence behavior: only `lolnd_instanced` persists in memory to prevent multiple loopback instances. No device, socket, or disk state exists. Message and MD state is delegated to core parser/finalizer code.

Dependencies/integration points: integrates with LNet LND registration, `lnet_parse()`, `lnet_copy_kiov2iter()`, `lnet_finalize()`, and NID string/type handling for `LOLND`.

Risks: this code assumes loopback messages never route and never target routers; violating those assertions is a core logic bug. Direct copy length uses `iov_iter_count(to)` and the send message offset/kiov fields, so parser setup must supply valid iterators. The single-instance flag is not separately locked and relies on LNet startup serialization.

Test signals: configure loopback once, reject/detect duplicate startup by assertion in debug builds, send local PUT/GET paths through parser, verify payload copy and both finalizers run, exercise discard receive path, and ensure shutdown clears the instance flag.
