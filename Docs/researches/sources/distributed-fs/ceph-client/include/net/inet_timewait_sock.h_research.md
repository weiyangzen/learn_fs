# sources/distributed-fs/ceph-client/include/net/inet_timewait_sock.h

Purpose: defines the compact INET TIME_WAIT socket representation and lifecycle helpers. It keeps enough 4-tuple, bind, mark, routing, timestamp, and policy state to enforce protocol TIME_WAIT semantics with lower memory use than a full socket.

Important APIs/types: `struct inet_timewait_sock` begins with `sock_common` and aliases family, state, refcount, hash nodes, addresses, ports, cookie, and net namespace. Additional fields store mark, substate, receive scale, source port, transparency, flowlabel/TOS, txhash, priority, entry timestamp, timer, bind buckets, optional PSP association, and optional xmit validation hook. APIs allocate/free/put, bind-unhash, schedule hashdance into time-wait, schedule/reschedule/deschedule timers, purge hash tables, and get/set namespace.

Control flow and state: connection close creates a time-wait object from the full socket, hashes it, schedules its timer, and eventually frees it after timeout or purge. State persists in bind/established hash tables and timer lists until expiry.

Dependencies and integration: depends on inet sock, sock, TCP states, timewait core, timers, workqueue, atomics, and inet hashinfo. It integrates with TCP close, connect conflict checks, port reuse, and namespace cleanup.

Risks: time-wait hashdance must not lose bind bucket references. Timer and refcount races can leak or use-after-free. Tests should cover allocation from full socket, hashdance, reschedule/deschedule, purge during namespace exit, bind unhash, reuse decisions, and optional validate-xmit hooks.
