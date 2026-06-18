# sources/distributed-fs/ceph-client/scripts/sign-file.c

Purpose: `sign-file.c` signs kernel modules by appending a PKCS#7/CMS signature, a `struct module_signature`, and the module signature marker. It can sign with PEM or PKCS#11 keys, append an externally generated raw signature, or save a detached signature.

Important APIs, types, and functions: `format()` prints usage. `pem_pw_cb()` supplies `KBUILD_SIGN_PIN` once to encrypted private keys. `read_private_key_pkcs11()` uses OpenSSL 3 providers or older engines. `read_private_key()` selects PKCS#11 URI versus PEM file. `read_x509()` detects DER versus PEM certificates. `main()` parses `-s`, `-d`, `-p`, and `-k`, prepares CMS flags, handles ML-DSA/OpenSSL 3.5 `CMS_NOATTR` compatibility, streams module bytes, writes signature data, `module_signature`, and marker, then optionally renames the signed temp over the original.

Control flow: raw-signature mode changes argument interpretation. Non-raw mode loads key/cert, resolves digest, creates a detached CMS signature over the module BIO, optionally writes `.p7s`, and may exit early for sign-only. Append mode writes the destination module copy before appending signature metadata.

State and persistence: it writes either an explicit destination or a temporary `module.~signed~` which is renamed over the module. `-p` writes `module.p7s`. It reads `KBUILD_SIGN_PIN` from the environment.

Dependencies and integration points: depends on OpenSSL headers/libraries, `ssl-common.h`, and `linux/module_signature.h`. Kbuild uses it for module signing and certificate workflows.

Risks: OpenSSL API compatibility is complex across 1.1, 3.x, providers, engines, PKCS#11, and post-quantum key handling. In-place signing has rename behavior but leaves temp files on some failures. Raw signatures are trusted as supplied and only length-stamped.

Test signals: sign/verify modules with PEM, encrypted PEM, PKCS#11, raw signatures, `-d`, `-p`, `-k`, DER and PEM certs, unknown digest, and OpenSSL 3 provider configurations. Kernel module loader acceptance is the integration test.
