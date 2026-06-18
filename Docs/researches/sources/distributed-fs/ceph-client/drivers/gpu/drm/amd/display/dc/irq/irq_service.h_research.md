# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.h

Purpose: internal IRQ service ABI shared by DCE/DCN interrupt service implementations.

Important APIs/types/functions: defines `struct irq_source_info_funcs` with optional `set` and `ack`; `struct irq_source_info` with source IDs, enable/ack/status registers, masks, values, and callback pointer; `struct irq_service_funcs` with `to_dal_irq_source`; and `struct irq_service` with context, table, and function table. Declares shared construct/generic set/generic ack and HPD ack helpers.

Control flow and integration: ASIC files allocate an `irq_service`, call `dal_irq_service_construct()`, assign a `const struct irq_source_info *info` table and `irq_service_funcs`, then the public IRQ service interface uses those fields to enable, ack, and translate sources.

State and persistence: declares the layout for service state but owns no storage. The `info` pointer is not owned by the service, so table lifetime is an integration contract.

Dependencies and risks: depends on `include/irq_service_interface.h` and `irq_types.h`. Structure layout changes affect every ASIC-specific IRQ service file. Callback NULL semantics mean generic behavior; dummy callback pointers intentionally trip warnings/assertions.

Test signals: full driver build across DCE/DCN variants and focused tests for generic set/ack behavior using populated `irq_source_info` instances.
