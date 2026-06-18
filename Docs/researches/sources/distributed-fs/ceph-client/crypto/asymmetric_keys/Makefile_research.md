# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Makefile

Purpose: maps asymmetric key Kconfig options to kernel objects and generated ASN.1 parser artifacts. It assembles compound modules such as `asymmetric_keys.o`, `x509_key_parser.o`, `pkcs7_message.o`, and PE verification support.

Important APIs/types/functions: `asymmetric_keys-y` combines `asymmetric_type.o`, `restrict.o`, and `signature.o`. X.509 support builds generated `x509.asn1.o` and `x509_akid.asn1.o` with parser/loader/public-key code. PKCS#8, PKCS#7, PKCS#7 test key, PE verification, and selftest objects are conditionally assembled from their sources.

Control flow: kbuild uses `obj-$(CONFIG_...)` to include objects, and explicit dependencies ensure generated ASN.1 headers exist before C parser objects compile. `clean-files` removes generated parser products.

State and persistence: no runtime state. Build products and generated ASN.1 C/header files are filesystem artifacts controlled by kbuild.

Dependencies and integration points: integrates with the kernel ASN.1 compiler, `crypto/asymmetric_keys/Kconfig`, generated parser definitions, key type registration, PKCS#7/X.509 verification, and selftest object inclusion.

Risks: dependency typos can race generated headers or leave stale generated files. Object grouping determines module boundaries and owner references used by parsers. The duplicated `mscode.asn1.h` prerequisite looks harmless but should be checked if dependency maintenance changes.

Test signals: clean builds after `make clean`, modular and built-in configurations for each parser, generated ASN.1 dependency ordering under parallel builds, and selftest object inclusion by config.
