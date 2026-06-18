# sources/distributed-fs/ceph-client/include/crypto/internal/geniv.h

Purpose: declares generic IV generator support for AEAD templates.

Important APIs, types, and flow: `aead_geniv_alloc()` creates a generic-IV AEAD instance from a crypto template and rtnetlink attributes; `aead_init_geniv()` initializes a `crypto_aead` transform with the selected generic-IV behavior.

State and persistence: generic-IV state is per instance and per transform; this header stores nothing directly and has no persistence.

Dependencies and integration: depends on AEAD template infrastructure and `struct rtattr`. It integrates with AEAD modes that derive IV handling through crypto templates.

Risks and test signals: risks include IV-size mismatch, bad template attribute parsing, and nonce reuse if geniv setup diverges from mode requirements. Signals include AEAD geniv template self-tests, instance creation with malformed attributes, and algorithm listings in `/proc/crypto`.
