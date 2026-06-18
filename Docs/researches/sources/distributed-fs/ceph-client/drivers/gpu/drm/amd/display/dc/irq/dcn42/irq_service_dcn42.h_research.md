# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.h

Purpose: DCN4.2 IRQ service interface, marked as dal-dev only in the file comment.

Important APIs/types/functions: declares `dal_irq_service_dcn42_create()`. Unlike most sibling headers, it includes `../dce110/irq_service_dce110.h` instead of `../irq_service.h`.

Control flow and integration: factory callers include this header to instantiate the DCN42 IRQ service.

State and persistence: no state.

Dependencies, risks, and test signals: the include choice couples this header to the DCE110 service header exporting or including the shared IRQ types. Build coverage should catch include-order regressions; runtime validation belongs to the C file.
