<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/geniv.c -->
# sources/distributed-fs/ceph-client/crypto/geniv.c

Purpose: Provides shared helper code for AEAD IV generator templates such as `seqiv`, wrapping a child AEAD while adding salt setup and common instance initialization.

Important APIs/types/functions: `aead_geniv_alloc()` creates an `aead_instance`, grabs the child AEAD, validates that the IV is at least `sizeof(u64)`, copies naming/priority/block/alignment/auth metadata, and installs common `setkey`/`setauthsize` forwarding. `aead_init_geniv()` obtains random salt with `crypto_stdrng_get_bytes()`, spawns the child, and sizes requests. `aead_exit_geniv()` frees the child. `aead_geniv_free()` drops the spawn and instance.

Control flow: A specific geniv template calls `aead_geniv_alloc()` during template create, then uses `aead_init_geniv()` and `aead_exit_geniv()` as its transform lifecycle hooks. Runtime key/authsize setters simply forward to `ctx->child`; actual IV construction is left to the specific generator implementation.

State and persistence behavior: `struct aead_geniv_ctx` in the transform context holds the child AEAD and generated salt. Salt persists for the transform lifetime only. Spawn references persist in the instance until the template instance is freed.

Dependencies and integration points: Uses internal AEAD and RNG APIs, crypto template attributes, rtnetlink-safe allocation context indirectly through kernel crypto users, and exports all three helper symbols GPL-only for other crypto modules.

Risks: IV size validation is minimal; generator-specific code must ensure nonce uniqueness. Failure cleanup must drop both child spawns and instances without double frees. Salt generation failure prevents transform initialization and must propagate to callers.

Test signals: Load geniv consumers, instantiate templates with valid and too-small-IV child AEADs, verify setkey/authsize forwarding, confirm request size accounts for child request plus wrapper request, and test salt randomness/failure paths with RNG availability issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/geniv.c -->
