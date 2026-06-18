# sources/distributed-fs/openafs/src/rx/HPUX/rx_knet.c

Purpose: HP-UX Rx kernel networking, including UDP interception for non-listener mode and socket send/receive wrappers for listener mode.

Important APIs/types/functions: global `rx_sleepLock`, `rxk_fasttimo`, `rxk_init`, `rxk_input`, `osi_NetSend`, and listener-mode `osi_NetReceive`.

Control flow: non-listener mode replaces UDP protosw input/timer, forces UDP checksumming, strips IP options, validates checksum including HP checksum-offload assist, converts mbufs to Rx packets, and falls back to original UDP. Send constructs STREAMS/socket address blocks and a kernel `uio` before calling `sosend`. Listener receive uses `soreceive`, copies sockaddr from returned message blocks, and clears socket errors on failure.

State/persistence: `parent_proto`, `rxk_initDone`, `rx_sleepLock`, Rx port arrays, and socket error state.

Dependencies/integration: HP-UX mbufs, STREAMS `MBLKP`, XTI, socket APIs, Rx packet hooks, and Rx event timer.

Risks: contains visible legacy bugs/typos in listener code (`tempvec` vs `tmpvec`) and old-style declarations; checksum-offload handling must clear flags correctly; protocol-switch patching is invasive. Test signals are HP-UX compile, UDP checksum/offload cases, Rx send/receive, and listener build path validation.
