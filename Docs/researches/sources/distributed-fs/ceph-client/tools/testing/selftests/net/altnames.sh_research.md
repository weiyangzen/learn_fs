# sources/distributed-fs/ceph-client/tools/testing/selftests/net/altnames.sh

Purpose: Tests network device alternative names through `ip link property` and JSON `ip link show`.

Important APIs/types/functions: Sources forwarding `lib.sh`, defines `ALL_TESTS=altnames_test`, creates a dummy device, uses `ip link property add/del ... altname`, `ip -j -p link show`, `jq`, and kselftest `check_err/check_fail/log_test`.

Control flow: Setup creates `dummytest`. The test adds a short altname, verifies lookup by altname and JSON reporting, verifies lookup by original name, adds a long altname, verifies it appears as the second altname, deletes the short altname, and confirms lookup by the deleted name fails. Cleanup deletes the dummy device.

State and persistence behavior: Alters a temporary dummy netdevice's altname list. No persistent state remains after device deletion.

Dependencies and integration points: Requires iproute2 altname support, dummy netdevice support, `jq`, and forwarding lib helpers.

Risks: Assumes JSON altname array ordering matches insertion order. If cleanup fails, the dummy device can remain.

Test signals: Passing output confirms add/show/delete altname behavior and JSON visibility for short and long altnames.
