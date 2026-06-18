<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_signature.h -->
# sources/distributed-fs/ceph-client/include/linux/module_signature.h

## Purpose
`module_signature.h` declares module signature validation support.

## Important APIs, Types, and Functions
It includes UAPI `struct module_signature` and declares `mod_check_sig(const struct module_signature *ms, size_t file_len, const char *name)`.

## Control Flow and State
The module loader reads appended signature metadata from a module file and calls `mod_check_sig()` with the signature descriptor, total file length, and module name. The implementation validates bounds and cryptographic signature data elsewhere.

## State and Persistence Behavior
Signature data is persisted in the module file. Runtime validation result is reflected in module loading policy and `struct module::sig_ok` when module signature support is enabled.

## Dependencies and Integration Points
It integrates with the module loader, public-key/keyring verification, UAPI signature layout, and module signature enforcement policy.

## Risks
Incorrect file length or descriptor validation can allow malformed modules, reject valid modules, or misreport signature status. It is security-sensitive and must be tested with enforcement enabled and disabled.

## Test Signals
Load signed, unsigned, truncated, and tampered modules; verify enforcement and permissive modes; and check error reporting names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_signature.h -->
