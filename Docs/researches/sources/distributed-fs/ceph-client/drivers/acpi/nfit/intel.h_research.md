# sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.h

`intel.h` defines the Intel NFIT DSM ABI consumed by `core.c` and `intel.c`. It contains Intel SMART shutdown fields, security command payloads and status codes, security state bits, firmware activation command payloads, activation state/result/capability constants, and extern declarations for Intel libnvdimm ops.

Key types include `struct nd_intel_smart`, `struct nd_intel_get_security_state`, passphrase mutation/unlock/disable/erase/overwrite structs, `struct nd_intel_fw_activate_dimminfo`, `struct nd_intel_fw_activate_arm`, `struct nd_intel_bus_fw_activate_businfo`, and `struct nd_intel_bus_fw_activate`. Constants such as `ND_INTEL_PASSPHRASE_SIZE`, `ND_INTEL_SEC_STATE_*`, `ND_INTEL_DIMM_FWA_*`, and `ND_INTEL_BUS_FWA_*` drive status translation and command construction.

There is no runtime control flow or owned state. The header defines packed binary layouts for transient DSM buffers and public ops pointers `intel_security_ops`, `intel_fw_ops`, and `intel_bus_fw_ops`.

Dependencies are libnvdimm ops declarations and the Intel NFIT DSM specification. Risks are field layout drift, packed-size mistakes, and context-sensitive status collisions such as overwrite unsupported versus overwrite-query in-progress. Test signals include sizeof/layout assertions where practical, command-specific status translation tests, SMART shutdown flag parsing, and build coverage for all Intel security/firmware paths.
