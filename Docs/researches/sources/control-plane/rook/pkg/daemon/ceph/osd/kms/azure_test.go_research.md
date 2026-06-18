# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure_test.go

This test file validates Azure Key Vault certificate preparation against a fake Kubernetes client.

`Test_AzureKVCert` runs three subtests. The first omits `AZURE_CERT_SECRET_NAME` and expects an error. The second provides a secret name that does not exist, while a differently named Secret is present, and expects an error. The third creates a matching Secret with `CLIENT_CERT` data, calls `azureKVCert()`, asserts the returned config contains an existing `azure.AzureClientCertPath`, then invokes the cleanup function and asserts the file is gone.

State is a fake Kubernetes Secret store and a temporary certificate file. Dependencies include Rook's operator test clientset, Kubernetes core Secret types, and libopenstorage Azure constants.

The test is a good signal for required Kubernetes secret wiring and temp-file cleanup. It does not initialize the actual Azure client, validate certificate contents, test write failures, or check behavior when the `CLIENT_CERT` key is absent. It also does not validate the mandatory connection details list beyond the certificate secret path.
