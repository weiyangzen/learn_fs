# sources/distributed-fs/ceph-client/drivers/cxl/security.c

Purpose: implements libnvdimm security operations for CXL PMEM devices using CXL mailbox security commands.

Important APIs/types/functions: `cxl_pmem_get_security_flags()`, `cxl_pmem_security_change_key()`, `__cxl_pmem_security_disable()`, user/master disable wrappers, `cxl_pmem_security_freeze()`, `cxl_pmem_security_unlock()`, `cxl_pmem_security_passphrase_erase()`, and exported `cxl_security_ops`.

Control flow and state: operations translate libnvdimm passphrase types into CXL user/master passphrase payloads, copy fixed-length passphrase data into packed CXL command structures, send mailbox commands via `cxl_internal_send_cmd()`, and map CXL security-state bits into nvdimm security flags. `get_flags()` caches the last CXL security state in `mds->security.state`.

Dependencies and integration: depends on libnvdimm security APIs, CXL mailbox definitions, CXL PMEM NVDIMM provider data, and fixed NVDIMM passphrase length constants. It is consumed by `pmem.c` when creating CXL-backed nvdimms.

Risks and test signals: passphrase type translation, state-flag mapping, failed mailbox command behavior returning no flags, and sensitive stack buffers are key. Test user and master passphrase flows, frozen/locked/disabled state mapping, wrong passphrase errors, unlock/erase semantics, unavailable security commands, and mailbox return-code propagation.
