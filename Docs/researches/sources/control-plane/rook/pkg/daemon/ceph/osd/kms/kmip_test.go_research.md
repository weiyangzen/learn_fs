# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip_test.go

This test file validates the first layer of KMIP configuration checks.

`TestInitKMIP` table-tests missing endpoint, missing CA certificate, missing client certificate, and missing client key. Each case calls `InitKMIP()` with progressively more config and asserts the exact sentinel error returned: `ErrKMIPEndpointNotSet`, `ErrKMIPCACertNotSet`, `ErrKMIPClientCertNotSet`, or `ErrKMIPClientKeyNotSet`.

State is in-memory configuration only. Dependencies are the local KMIP KMS package and `testify/assert`. The test deliberately stops before valid TLS material, so it does not exercise certificate parsing, timeout parsing, maximum timeout bounds, TLS config creation, connection setup, KMIP discover, TTLV request/response handling, register/get/delete, or response verification.

The useful signal is that required secret/token details fail fast with stable errors. Significant integration risk remains around live KMIP interoperability and the lower-level protocol code, which would require a KMIP test server or carefully constructed TTLV fixtures to validate.
