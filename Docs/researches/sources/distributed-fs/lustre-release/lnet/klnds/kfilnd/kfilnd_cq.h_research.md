<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h_research.md`.

Purpose: declares the completion-queue interface used by endpoints and fail-location error injection.

Important APIs/types/functions: exports `kfilnd_cq_process_error()`, `kfilnd_cq_alloc()`, and `kfilnd_cq_free()` over `struct kfilnd_ep`, `struct kfi_cq_err_entry`, `struct kfi_cq_attr`, and `struct kfilnd_cq`.

Control flow: endpoint allocation calls `kfilnd_cq_alloc()` for RX and TX CQs; endpoint teardown calls `kfilnd_cq_free()`; fake endpoint errors can call `kfilnd_cq_process_error()` asynchronously.

State and persistence behavior: no state is defined here beyond function contracts; concrete CQ state is in `kfilnd.h` and `kfilnd_cq.c`.

Dependencies and integration: includes `kfilnd.h`, so it inherits kfabric and LNet private structures.

Risks: this header exposes error processing, so callers must only pass provider-shaped error records and live endpoints.

Test signals: compile inclusion from endpoint and CQ modules, inject fake errors through `kfilnd_ep_gen_fake_err()`, and verify RX/TX CQ allocation/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h -->
