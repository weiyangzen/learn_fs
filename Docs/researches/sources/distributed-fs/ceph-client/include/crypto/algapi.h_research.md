# sources/distributed-fs/ceph-client/include/crypto/algapi.h

Purpose: low-level kernel crypto algorithm/template registration and queue helper API.

Important APIs/types/functions: max block/align constants, `CRYPTO_DMA_ALIGN`, `MODULE_ALIAS_CRYPTO`, `struct crypto_instance`, `struct crypto_template`, `struct crypto_spawn`, `struct crypto_queue`, `struct scatter_walk`, registration/unregistration functions for algorithms/templates/instances, spawn helpers, attr parsing helpers, crypto queue operations, `crypto_inc`, tfm/instance context helpers, inherited flag helpers, notifier APIs, `crypto_request_complete`, and request flag/type helpers.

Control flow: algorithm providers register `crypto_alg` objects or templates; templates grab child spawns, create instances, and register them. Async providers enqueue/dequeue requests and complete callbacks through `crypto_request_complete`.

State and persistence: registration creates global crypto algorithm/template state. Queues track pending requests and backlog. Instances contain private context and spawn relationships.

Dependencies and integration points: foundational for all crypto providers, templates, and async engines. Depends on list, workqueue, module, and crypto core structures.

Risks: registration lifetime, module references, and spawn `dead/registered` transitions are subtle. Incorrect inherited flag masking can expose blocking or fallback behavior incorrectly. Queue backlog handling affects async caller semantics.

Test signals: crypto manager registration tests, template instance creation/removal tests, module autoload alias checks, async queue/backlog tests, and lockdep around provider unregister paths.
