## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_csbcpb.h

Purpose: defines the packed NX coprocessor status block and coprocessor parameter block layouts for AES, AEAD, XCBC, SHA256, and SHA512 operations, plus mode/function constants used by the NX crypto wrappers.

Important structures and macros: `struct cop_symcpb_*` variants model per-mode CPB payloads. `struct cop_symcpb_header`, `struct cop_parameter_block`, `struct cop_status_block`, and `struct nx_csbcpb` define the complete hardware page layout. Macros such as `NX_CPB_FDM`, `NX_CPB_SET_KEY_SIZE`, `NX_CPB_SET_DIGEST_SIZE`, `NX_CSB_VALID_BIT`, mode constants, FDM continuation/intermediate/encrypt flags, function codes, key sizes, digest sizes, and property indices are used throughout the NX driver.

Control flow and integration: wrappers fill the CPB header/mode/key/IV/state fields before calling `nx_hcall_sync`. The hypervisor/hardware writes the CSB and output CPB fields such as chaining values, message digests, counters, MACs, and processed-byte counts. `nx_ctx_init` sets the CSB valid bit and physical addresses for hcalls.

State and persistence: CPBs are per-transform runtime memory, but they contain sensitive key material and intermediate authentication/hash state. No fields are persisted outside kernel memory unless algorithm wrappers explicitly copy IVs/tags/digests to caller buffers.

Dependencies: exact packed layout expected by IBM NX hardware and pHyp. Includes no external headers beyond basic types through includers.

Risks: any structure padding, field size, or constant change can break hardware protocol. Union overlays mean wrappers must reference the correct member for the active mode. Key/digest size macros OR bits into `ks_ds`; callers must initialize/clear CPBs before reuse. Endianness of multi-byte CSB fields is hardware-defined and must be converted at use sites.

Test signals: build-time layout checks would be valuable, plus algorithm known-answer tests for every mode, hcall CSB processed-byte validation, key-size/digest-size selection tests, and static analysis for sensitive data lifetime.
