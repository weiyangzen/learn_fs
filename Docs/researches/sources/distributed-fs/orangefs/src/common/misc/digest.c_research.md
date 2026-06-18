<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/digest.c -->
# sources/distributed-fs/orangefs/src/common/misc/digest.c

Purpose: utility wrapper for cryptographic digests, currently SHA-1 and MD5. It uses OpenSSL when available and returns `-PVFS_EOPNOTSUPP` otherwise.

Important functions: the private `digest()` looks up an OpenSSL digest by name, allocates an `EVP_MAX_MD_SIZE` output buffer, initializes an EVP context, updates with caller data, finalizes into the allocated buffer, and returns the buffer plus length through output parameters. `PINT_util_digest_sha1()` and `PINT_util_digest_md5()` call it with `"sha1"` and `"md5"`.

Control flow is compile-time conditional. Under `HAVE_OPENSSL`, it supports both OpenSSL 1.1 heap-allocated `EVP_MD_CTX` and older stack contexts. Without OpenSSL, all digest calls return unsupported without touching output buffers.

State behavior: output buffer ownership transfers to caller on success. There is no persistent state. Dependencies include OpenSSL EVP APIs, OrangeFS error codes, and build macros `HAVE_OPENSSL`/`HAVE_OPENSSL_1_1`.

Risks: if `output` is NULL, the allocated digest buffer is not freed, causing a leak; the function still allocates even when only length is requested. OpenSSL init/provider requirements are not handled here. Digest algorithms MD5/SHA1 are not collision-resistant and should not be used for security decisions. Tests should cover OpenSSL/no-OpenSSL builds, invalid digest name via private test harness if exposed, NULL output/output_len combinations, known vectors, and caller frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/digest.c -->
