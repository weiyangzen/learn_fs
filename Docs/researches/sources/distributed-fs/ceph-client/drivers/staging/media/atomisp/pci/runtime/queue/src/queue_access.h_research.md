# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.h

Purpose: internal queue handle layout and remote access API declarations.

Important definitions/types: descriptor ignore flags and combined masks, `QUEUE_CB_DESC_INIT`, and `struct ia_css_queue` with type/location/proc id plus either local circular-buffer state or remote descriptor/element addresses.

Control flow/state: the macro initializes circular-buffer descriptors to zero before selective remote loads. Function declarations are implemented in `queue_access.c` and used by `queue.c`.

Dependencies/integration: depends on errno, type support, queue communication constants, and circular-buffer types.

Risks: public `ia_css_queue.h` includes this internal header, so changing `struct ia_css_queue` affects all users. Ignore flags must remain within `QUEUE_IGNORE_DESC_FLAGS_MAX` or assertions fire in access code.

Test signals: macro initialization behavior, ignore-mask combinations, ABI size/layout of `ia_css_queue_t`, and remote init populating the expected union fields.
