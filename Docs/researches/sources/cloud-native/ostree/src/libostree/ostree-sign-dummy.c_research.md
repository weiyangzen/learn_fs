# sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.c

Purpose: implements a test-only `OstreeSign` backend named `dummy`. It stores ASCII strings as secret/public keys and treats the secret string bytes as the signature, allowing signing pipeline tests without cryptographic dependencies.

Important APIs/types/functions: `OstreeSignDummy` stores `sk_ascii` and `pk_ascii`. `check_dummy_sign_enabled` requires `OSTREE_DUMMY_SIGN_ENABLED=1`. Interface init wires name, data sign/verify, metadata key/format, and key setters, mapping `add_pk` to `set_pk`. Signing returns secret-string bytes. Verification checks metadata type `aay`, iterates signatures, and succeeds when any signature string equals the public key string.

Control flow: signing and verification enforce the environment guard. Signing assumes a secret key and creates bytes from the stored string. Verification rejects missing signatures or wrong type, converts each child to a string, logs candidate/stored values, and returns the first match or a descriptive failure.

State/persistence: key strings are stored in the object. Signatures are persisted by the generic signing layer into detached commit metadata or `summary.sig` under `ostree.sign.dummy`.

Dependencies/integration: depends on `OstreeSign`, GLib/GObject/GVariant/GBytes, libglnx, and string utilities. It is always included in the signing registry as the fallback/test engine.

Risks: it is intentionally not secure; the environment guard prevents ordinary use. `data` can crash if called before setting `sk_ascii`. `add_pk` replacement means multi-key semantics differ from real engines. The implementation appears to lack explicit finalize cleanup for key strings.

Test signals: `tests/test-signed-commit-dummy.sh` signs, verifies detached metadata, commits with `--sign-type=dummy`, and checks verification without the enabling environment fails.
