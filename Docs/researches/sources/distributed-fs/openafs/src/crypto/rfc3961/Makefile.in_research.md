# sources/distributed-fs/openafs/src/crypto/rfc3961/Makefile.in

This Makefile builds OpenAFS' selected Heimdal Kerberos RFC3961 crypto library. It installs `rfc3961.h`, compiles local shims `context.c` and `copy.c`, then compiles selected upstream Heimdal `krb5` crypto/data/keyblock/n-fold/store files into shared, PIC, and LWP/static archives.

Control flow is make target driven: `all` builds the installed header, shared `liboafs_rfc3961.la`, PIC archive, and `libafsrfc3961.a`; `install`/`dest` stage the static library; explicit rules compile upstream sources through `LTLWP_CCRULE`. State is generated archives, libtool objects, and installed headers.

Dependencies include hcrypto, roken, upstream Heimdal krb5 sources, OpenAFS make fragments, and warning-workaround CFLAGS for selected sources. Integration points are rxgk/security code and any Kerberos crypto consumer that uses the OpenAFS-renamed RFC3961 API. Risks include incomplete upstream source selection, algorithm lists diverging from header-advertised enctypes, and static/shared symbol conflicts. Test signals are Kerberos RFC3961 known-answer vectors and downstream link tests against hcrypto.
