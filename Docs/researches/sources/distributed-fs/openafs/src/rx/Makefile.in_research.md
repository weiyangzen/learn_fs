# sources/distributed-fs/openafs/src/rx/Makefile.in

Purpose: builds the userspace Rx protocol libraries and installs public Rx headers.

Important APIs/types/functions: object list `LT_objs`, targets `all`, `depinstall`, `includes`, `librx.a`, `liboafs_rx.la`, `librx_pic.la`, `install`, `dest`, `clean`, and numerous header install rules under `TOP_INCDIR/rx`.

Control flow: includes OpenAFS config/LWP make fragments, compiles XDR, call, connection, event, packet, peer, stats, multi-call, and support objects, builds static/shared/PIC convenience libraries, installs headers, and recurses into `test` and examples during clean.

State/persistence: generated libraries in build/top lib directories, installed headers, and generated component version source.

Dependencies/integration: depends on `liboafs_opr`, thread libraries, libtool wrappers, LWP build rules, and Rx source/header dependency declarations.

Risks: typo-preserved object `xdr_refernce.lo` must match source name; header install list must track public API additions; clean recurses into example directories. Test signals are `make all`, `make install`, link of libafsrpc users, and consumers compiling against installed headers.
