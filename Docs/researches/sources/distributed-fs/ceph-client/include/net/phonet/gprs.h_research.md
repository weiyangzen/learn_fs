# sources/distributed-fs/ceph-client/include/net/phonet/gprs.h

Purpose: declares the GPRS-over-Phonet pipe endpoint hooks used by PEP sockets to expose readable/writable data paths.

Important APIs and types: forward declarations for `sock` and `sk_buff`; functions `pep_writeable()`, `pep_write()`, `pep_read()`, `gprs_attach()`, and `gprs_detach()` form the minimal interface.

Control flow: a Phonet/PEP socket attaches GPRS handling to a socket, checks writability, writes skbs into the pipe endpoint, reads received skbs, and detaches on teardown.

State and persistence: state is maintained in the PEP/GPRS socket implementation, not this header. It is connection-lifetime only.

Dependencies and integration points: integrates Phonet pipe endpoint sockets with GPRS network data handling and skbuff ownership.

Risks and test signals: risks include attach/detach lifetime mismatches, writeability races with pipe flow control, and skb ownership leaks. Test GPRS attach/detach, read/write under credit changes, socket close with queued skbs, and error paths.
