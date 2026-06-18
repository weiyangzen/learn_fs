# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.h

Purpose: declares Loongson display-controller IRQ handlers.

Important APIs/types/functions: prototypes for `ls7a1000_dc_irq_handler` and `ls7a2000_dc_irq_handler`.

Control flow: chip descriptors reference these handlers through `lsdc_kms_funcs`.

State and persistence: no state in the header.

Dependencies and integration points: includes IRQ return types and local driver definitions.

Risks and test signals: prototype mismatch would break descriptor initialization. Test build and IRQ registration.
