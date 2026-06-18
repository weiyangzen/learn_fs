# sources/distributed-fs/ceph-client/include/crypto/internal/aead.h

Purpose: provides private AEAD registration, template-instance, spawn, queue, context, and request-size helpers for authenticated encryption algorithms.

Important APIs, types, and flow: `struct aead_instance` overlays `struct crypto_instance` with `struct aead_alg` for template-produced algorithms. `struct crypto_aead_spawn` binds a template instance to an inner AEAD algorithm via `crypto_grab_aead()` and later instantiates it through `crypto_spawn_aead()`. Inline helpers retrieve transform, instance, request, and DMA-aligned request contexts; complete requests; initialize AEAD queues; set normal or DMA-padded request sizes; and expose AEAD chunk size. `crypto_register_aead*()` and `aead_register_instance()` publish algorithms and template instances.

State and persistence: state is held in crypto transform contexts, request contexts, queue entries, and template instance memory. No external persistence exists.

Dependencies and integration: integrates public `crypto/aead.h`, `crypto/algapi.h`, generic spawn/instance infrastructure, and callers implementing AEAD templates such as authenc, CCM/GCM wrappers, or hardware adapters.

Risks and test signals: incorrect `offsetof()` overlay assumptions, DMA alignment padding, request-size underestimation, or chunk-size reporting can corrupt request private data or break streaming AEAD modes. Test signals include crypto manager AEAD self-tests, DMA-aligned hardware drivers, template load/unload tests, and async queue completion ordering.
