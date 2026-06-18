<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h_research.md`.

Purpose: exposes the small public domain lifecycle API to device allocation code.

Important APIs/types/functions: `kfilnd_dom_get()` returns a referenced `struct kfilnd_dom` plus caller-owned `struct kfi_info`; `kfilnd_dom_put()` releases domain and fabric references.

Control flow: device startup calls get before AV/SEP creation; device teardown calls put after closing device KFI objects.

State and persistence behavior: the header defines no state, but its API owns fabric/domain reference transitions.

Dependencies and integration: includes `kfilnd.h` for LNet NI, domain, and kfabric info types.

Risks: callers must free the returned `kfi_info` and must pair every successful get with put. Passing invalid NI or output pointer returns error pointers.

Test signals: compile device code, startup/shutdown under repeated NI creation, and inject failures after get to confirm put/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h -->
