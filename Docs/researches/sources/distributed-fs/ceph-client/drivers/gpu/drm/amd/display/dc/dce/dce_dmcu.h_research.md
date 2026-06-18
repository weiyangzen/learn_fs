# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.h

Purpose: defines DCE/DCN DMCU register lists, mask/shift field lists, the `struct dce_dmcu` wrapper, PSR command-data packing unions, and constructors/destructor for generation-specific DMCU implementations.

Important APIs and types: register-list macros cover DCE base, DCE60, DCE80, DCE110, DCN10, and DCN20 register sets. `DMCU_REG_FIELD_LIST()` generates shift/mask structs. `struct dce_dmcu_registers` contains DMCU control/status, IRAM access, master/slave mailbox, interrupt, scratch, and memory-power registers. `struct dce_dmcu` embeds `struct dmcu`. PSR unions `dce_dmcu_psr_config_data_reg1/2/3` and `dce_dmcu_psr_config_data_wait_loop_reg1` define the exact mailbox bit layout for firmware commands.

Control flow and integration: the header is used by ASIC resource files to pass correct register tables into `dce_dmcu.c`. Generic DC code sees only `struct dmcu` and its function table, while this header preserves the DCE-specific packing contract required by DMCU firmware.

State and persistence: no external persistence. The object persists context, function table, cached wait loop, firmware state/version fields inherited from `struct dmcu`, and register metadata. Mailbox union layouts are persistent ABI with DMCU firmware and must not drift.

Dependencies and risks: depends on `dmcu.h` and generated register names. Risks include bitfield layout portability/ABI assumptions, comments that mention a mismatched closing guard (`_DCE_ABM_H_`), and generation macros omitting fields used by newer code paths. Test signals include compile coverage for SI/non-SI configs, PSR command binary compatibility, DMCU construction on DCE/DCN families, and register table validation for optional `DMCUB_SCRATCH15`.
