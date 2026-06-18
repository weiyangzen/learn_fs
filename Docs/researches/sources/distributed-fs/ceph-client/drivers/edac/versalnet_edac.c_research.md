# sources/distributed-fs/ceph-client/drivers/edac/versalnet_edac.c

Purpose: `versalnet_edac.c` supports AMD Versal NET DDRMC5 EDAC using RPMsg and CDX MCDI firmware communication. It registers up to eight DDR5 controllers, handles firmware error payloads, reports DDR CE/UE events, logs non-DDR RAS events, and can call `memory_failure()` for UE pages.

Important APIs/types/functions: `struct mc_priv` stores message/status fields, register/ADEC arrays, per-controller `mci[]`, RPMsg endpoint, and MCDI handle. `get_ddr_info()` parses controller register slices. `convert_to_physical()` applies ADEC/interleave/offset math. `handle_error()` reports EDAC and poisons UE pages. `rpmsg_cb()` handles MCDI responses, split payloads, DDR IDs 18/19, and non-DDR RAS logs.

Control flow: probe gets and boots the R5 remote processor, allocates shared state, registers RPMsg, initializes MCDI, fetches DDR config for all controllers, and registers each enabled MC. RPMsg callbacks assemble payloads, dispatch DDR CE/UE across controller slices, or log non-DDR events. Remove unregisters RPMsg, removes MCs, shuts down remoteproc, and frees MCDI.

State and persistence: one `mc_priv` persists for the platform lifetime; ADEC data is cached; partial messages use `part_len` and `regs`. No disk persistence exists.

Dependencies/integration: OF compatible `xlnx,versal-net-ddrmc5`, `amd,rproc`, remoteproc, RPMsg `error_ipc`, CDX MCDI protocol, EDAC, RAS event logging, and optional memory failure.

Risks: removal/rollback can dereference null `mci[]` for skipped controllers; `dwidth` is shared across controllers; group-bit address reconstruction appears to use bank fields; global RPMsg driver data is single-instance; partial payload bounds are not obvious.

Test signals: remoteproc/RPMsg boot, MCDI config retrieval, split-message assembly, CE/UE IDs 18/19, non-DDR RAS logging, page poisoning, skipped-controller remove paths, and teardown.
