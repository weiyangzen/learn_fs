# sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/test-dm-verity-keyring.sh

## Purpose

`test-dm-verity-keyring.sh` validates dm-verity `.dm-verity` keyring behavior in unsealed/signature-required mode and default sealed mode. It checks key upload, keyring sealing, multiple trusted keys, unknown/corrupt signature rejection, sealed-keyring rejection of new keys, and behavior of an empty inactive keyring.

## Important APIs, Types, and Functions

It uses `modprobe`, `dmsetup`, `veritysetup`, `keyctl`, `openssl`, `losetup`, `dd`, `/proc/keys`, `/sys/module/dm_verity/parameters/*`, PKCS#7 detached signatures, X.509 certs, loop devices, and temporary dm targets. Major functions include `cleanup()`, `find_dm_verity_keyring()`, `check_requirements()`, `load_dm_verity_module()`, `generate_named_key()`, `upload_named_key()`, `seal_keyring()`, `create_test_device()`, `create_verity_hash()`, `create_detached_signature()`, `activate_verity_device()`, `sign_root_hash_with_key()`, `test_multiple_keys()`, `test_corrupted_signature()`, `test_keyring_sealed_by_default()`, and `test_keyring_inactive_when_empty()`.

## Control Flow

`main()` creates a work directory, validates tools/root/module availability, loads dm-verity with `keyring_unsealed=1 require_signatures=1`, uploads three generated certs, seals the keyring, creates data/hash loop devices, formats verity metadata, verifies signatures from all trusted keys, verifies an unknown key fails, verifies sealed keyring rejects further keys, and tests truncated/corrupt/wrong-data signatures. It then cleans loop devices, reloads dm-verity with `keyring_unsealed=0 require_signatures=0`, checks the keyring is sealed by default, and verifies empty-keyring behavior.

## State and Persistence Behavior

The script mutates loaded kernel modules, module parameters, `.dm-verity` keyring contents/restrictions, loop devices, dm targets, temporary files, generated certs/keys/signatures, and dmesg visibility. `trap cleanup EXIT` removes dm targets, loop devices, and temp directories.

## Dependencies and Integration Points

It depends on root, module unload support, dm-verity keyring parameters, keyutils, OpenSSL `smime`, cryptsetup `veritysetup`, loop devices, and device mapper. It integrates kernel keyrings, asymmetric certificate parsing, PKCS#7 verification, and dm-verity table activation.

## Risks and Edge Cases

The script unloads/reloads `dm-verity`, which fails if any dm-verity target is in use. It parses `/proc/keys` and converts hex serials, which requires permission and stable output. Test signatures intentionally omit embedded certs (`-nocerts`), requiring keyring matching to work. The script uses `set -e` but many tests capture return codes carefully.

## Test Signals

Pass signals are successful activation with each trusted key, failed activation with unknown/truncated/corrupt/wrong signatures, failed key addition after sealing, expected activation behavior with empty sealed keyring, and final all-tests-passed summary. Failures identify keyring, signature, module, or dm target regressions.
