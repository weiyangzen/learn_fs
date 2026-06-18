# sources/distributed-fs/ceph-client/kernel/module/signing.c

## Purpose
Performs module signature detection, PKCS#7 signature verification, and signature enforcement policy for module loads.

## Important APIs, Types, And Functions
Exports `is_module_sig_enforced` and `set_module_sig_enforced`. Internal entry points are `mod_verify_sig` and `module_sig_check`. The runtime parameter `module.sig_enforce` can only enable enforcement.

## Control Flow
`module_sig_check` detects the appended module signature marker unless the module was mangled by ignore-vermagic or ignore-modversions flags. It strips the marker, calls `mod_verify_sig`, and sets `info->sig_ok` on success. Unsigned, unsupported-crypto, or missing-key cases are rejected when enforcement is active; otherwise lockdown policy decides. Other verification errors are fatal even without enforcement.

## State And Persistence
State is `sig_enforce` and `load_info.sig_ok`. `mod_verify_sig` also shortens `info->len` so subsequent ELF parsing ignores the appended signature.

## Dependencies And Integration Points
Depends on `module_signature.c` for trailer sanity, PKCS#7 verification, secondary keyring use, LSM lockdown, module parameters, and `uapi/linux/module.h` flags. It is called at the start of `load_module`.

## Risks And Edge Cases
Forced/mangled modules must not be accepted as signed because stripped metadata invalidates the signature. Signature length arithmetic must prevent trailer underflow/overflow. Enforcement and lockdown interactions determine whether unsigned modules are rejected or merely taint later in `main.c`.

## Test Signals
Load signed, unsigned, bad-signature, missing-key, unsupported-crypto, and mangled modules under enforcing and permissive configs. Verify `info->len` truncation and `TAINT_UNSIGNED_MODULE` behavior downstream.
