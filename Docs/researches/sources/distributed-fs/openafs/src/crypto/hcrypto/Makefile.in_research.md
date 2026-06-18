# sources/distributed-fs/openafs/src/crypto/hcrypto/Makefile.in

This Makefile builds OpenAFS' trimmed Heimdal hcrypto library. It includes config/lwp make fragments, defines libtool versioning, object lists for AES, Camellia, DES, EVP, HMAC, hashes, random, RC2/RC4, UI, and validation sources, and installs selected hcrypto headers into `TOP_INCDIR`.

Control flow is make target selection: `all-internal`, `all-lwp`, and `buildtools` install headers and build shared/static/LWP archives; `install` and `dest` stage `libafshcrypto.a` and optional shared libraries; explicit object rules compile sources from `external/heimdal/hcrypto` because implicit rules cannot find them. State is generated archives, libtool objects, installed headers, and optional test binary `test_cipher`.

Dependencies are Heimdal upstream sources, roken, libtool macros, OpenAFS make fragments, and `@hcrypto_all_target@`/`@hcrypto_install_target@` substitutions. Integration points are `rfc3961`, rxgk/rxkad crypto consumers, kernel-adapted hcrypto builds, and buildtools. Risks include upstream source drift, object/header list mismatch, intentionally disabled warnings for selected sources, and shared/static target divergence. Test signals are successful `libafshcrypto` builds, header installation, `test_cipher`, and downstream RFC3961 link tests.
