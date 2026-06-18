# sources/distributed-fs/ceph-client/tools/bpf/bpftool/sign.c

Purpose: Provides OpenSSL and keyring support for signed generated-loader execution in bpftool. It reads a private key and certificate, creates a detached CMS signature over loader instructions, computes the SHA-256 program hash, and can add the certificate to the session keyring.

Important APIs, types, and functions: `display_openssl_errors()` drains OpenSSL error details. `read_private_key()` reads PEM private keys. `read_x509()` accepts DER or PEM X.509 by probing the first bytes. `register_session_key()` converts the X.509 certificate to DER and calls `add_key("asymmetric", ..., KEY_SPEC_SESSION_KEYRING)`. `bpftool_prog_sign()` builds a CMS object with `CMS_NOCERTS`, `CMS_BINARY`, `CMS_DETACHED`, `CMS_USE_KEYID`, and `CMS_NOATTR`, fills `opts->excl_prog_hash`, `opts->signature`, and `opts->signature_sz`.

Control flow: Signing starts with an in-memory BIO for `opts->insns`, loads `private_key_path` and `cert_path`, creates a partial CMS, adds one signer, finalizes over the instruction BIO, hashes the instruction bytes, DER-encodes CMS to a memory BIO, validates signature buffer capacity, copies the signature to caller storage, and frees OpenSSL objects.

State and persistence: The signing path mutates the caller's `bpf_load_and_run_opts` buffers. `register_session_key()` persists the certificate in the process session keyring. No local files are written.

Dependencies and integration points: Used by `prog.c` generated-loader path. Depends on OpenSSL EVP, BIO, X509, PEM, CMS APIs and Linux `add_key` syscall. Global `private_key_path` and `cert_path` are supplied by bpftool option parsing.

Risks: Certificate format detection is heuristic; DER is assumed from ASN.1 SEQUENCE length bytes. CMS signature length can exceed `opts->signature_sz`. The code reports OpenSSL errors only when OpenSSL has queued errors, so syscall failures rely on errno. Session key insertion requires keyring permissions and a valid asymmetric key parser in the kernel.

Test signals: Unit-style tests can feed PEM/DER certs, invalid files, undersized signature buffers, and missing private keys. Integration needs generated-loader signing with `bpftool prog load -L -S -k key -i cert` and verification that the session key is registered.
