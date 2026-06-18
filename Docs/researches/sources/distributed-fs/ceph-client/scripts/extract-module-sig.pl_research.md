# sources/distributed-fs/ceph-client/scripts/extract-module-sig.pl

Purpose: Extracts selected portions of an appended Linux kernel module signature.

Important APIs/functions: Reads an entire module, validates the magic string `~Module signature appended~\n`, unpacks the 12-byte descriptor with `unpack("CCCCCxxxN", ...)`, slices signer name, key id, signature/PKCS#7 message, unsigned module, and full signature trailer. Options are `-0`, `-a`, `-d`, `-n`, `-k`, and `-s`.

Control flow: Validates two arguments, reads the module in binary mode, checks minimum length, finds the magic at EOF, backs up over descriptor and variable-length name/key/signature regions, prints diagnostics to stderr, and writes the requested binary or textual part to stdout.

State/persistence: No persistent state. Reads whole input into memory and writes requested output to stdout.

Dependencies/integration: Perl core only. Integrated with module signing diagnostics and tooling.

Risks: Unknown option values fall through without explicit error after parsing, producing no output. Entire module read can be large. It trusts descriptor lengths after one aggregate bounds check.

Test signals: Signed module fixtures for each output part, unsigned/too-short module, PKCS#7 id type warnings for name/key, unsupported id type, and malformed descriptor lengths.
