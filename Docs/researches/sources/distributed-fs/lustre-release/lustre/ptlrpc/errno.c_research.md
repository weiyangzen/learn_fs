# sources/distributed-fs/lustre-release/lustre/ptlrpc/errno.c

Purpose: provides optional host-to-network and network-to-host errno translation for Lustre wire compatibility when `LUSTRE_TRANSLATE_ERRNOS` is enabled. It exists because Linux errno numeric values are not fully portable across architectures, while Lustre RPC replies need stable on-wire status values.

Important APIs/types/functions: `lustre_errno_hton()` maps a local positive errno value to a `LUSTRE_E*` value; `lustre_errno_ntoh()` maps back to the host errno namespace; both are exported symbols. The static `lustre_errno_hton_mapping[]` and `lustre_errno_ntoh_mapping[]` tables are designated-initializer arrays intended to be one-to-one. They include normal POSIX/Linux errors, Lustre-specific network errors such as `EBADHANDLE`, and LDLM-specific `ELDLM_*` values that intentionally preserve their numeric range.

Control flow: callers pass unsigned errno magnitudes, not negative return codes. Zero maps to zero. If an index is in range and populated, the table value is returned. If the value is out of range or maps to zero, control falls to a generic path that returns `LUSTRE_EIO` or `EIO` to avoid interpreting an unknown numeric errno as a different meaning on another host.

State/persistence: no mutable runtime state and no persistence. The ABI-relevant state is the compiled mapping table. Changing table values changes wire semantics.

Dependencies/integration: depends on `lustre_errno.h`; under translation it also includes `lustre_dlm.h` for `ELDLM_*` values. Integrated with PTLRPC packing/unpacking paths that put status codes on the wire.

Risks/test signals: table gaps silently degrade to I/O error, which is safe but loses specificity. Architecture-specific aliases are explicitly called out: `EDEADLOCK` is avoided in favor of `EDEADLK`. Tests should verify round trips for representative POSIX errors, Lustre private errors, LDLM errors, zero, unknown high values, and table entries that are unavailable on a given architecture.
