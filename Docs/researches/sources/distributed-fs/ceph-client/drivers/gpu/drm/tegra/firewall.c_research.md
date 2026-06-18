# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/firewall.c

Purpose: validates host1x command streams before submission so jobs cannot program engine address registers with IOVAs outside the mappings supplied for that submit.

Important APIs/functions: `tegra_drm_fw_validate()` walks command words from a gather, tracks current class and extended payload length, decodes host1x opcodes, and dispatches register validation. `fw_check_reg()` asks the client whether a register offset is address-bearing and validates the following data word. `fw_check_regs_seq()`, `fw_check_regs_mask()`, and `fw_check_regs_imm()` handle sequential, mask, and immediate write forms. `fw_check_class()` constrains class switches via client callbacks or the client base class.

Control flow and state: the validator keeps a cursor over command data (`pos/end`), current host1x class, submit mapping table, and payload state for wide opcodes. Valid SETCLASS updates `*job_class`, preserving class across gathers/jobs as expected by callers.

Dependencies/integration: depends on `tegra_drm_client_ops.is_addr_reg`, optional `is_valid_class`, submit mapping records, and host1x opcode encoding.

Risks: only recognized write opcodes are allowed; gather/restart/stream/appid opcodes are rejected here. Address validation accepts offsets inclusively between `m->iova` and `m->iova_end`, so mapping end semantics must match the submit mapping code. `SETPYLD` payload state is sticky until overwritten.

Test signals: submit tests should cover legal address writes, out-of-range IOVAs, IMM writes to address registers, invalid classes, SETCLASS masks, INCR_W/NONINCR_W without payload, and unsupported opcodes.
