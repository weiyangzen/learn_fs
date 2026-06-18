# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect_test.go

This test file validates IBM Key Protect client initialization rules.

`TestInitKeyProtect` uses a mutable config map across subtests. It first verifies that missing `IBM_KP_SERVICE_API_KEY` returns `ErrIbmServiceApiKeyNotSet`, then adds the key and verifies missing `IBM_KP_SERVICE_INSTANCE_ID` returns `ErrIbmInstanceIdKeyNotSet`. After adding the instance ID, it checks that omitted base URL defaults to `kp.DefaultBaseURL`, custom base URL is honored, omitted token URL defaults to `kp.DefaultTokenURL`, and custom token URL is honored.

State is only the in-memory config map and constructed IBM client object. Dependencies include the IBM Key Protect Go client and `testify/assert`.

The test signal is clear for required configuration and defaults. It does not perform network calls, authentication, secret CRUD, verbose logging behavior, or interaction with `ConfigToEnvVar()` secret redaction. Because the same map is reused across subtests, ordering matters, but the sequence is intentional and documents incremental configuration requirements.
